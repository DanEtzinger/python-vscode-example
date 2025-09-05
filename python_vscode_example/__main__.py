import socket
from datetime import timedelta

from dynatrace_extension import Extension, MetricType, Status, StatusValue

from .db_connection import SqliteDatabase


class ExtensionImpl(Extension):
    def initialize(self):
        """
        This is called only one time after the extension starts, and can be used to handle user input
        when configuring the extension, such as setting  the schedule frequency.
        """
        # Iterate through all endpoints confgured in the monitoring configuration
        for endpoint in self.activation_config["endpoints"]:
            try:
                # These next few lines are specific to the setup of the SQLite database
                # Set the user-entered 'dbname'
                # from the monitoring config in `extension/activationSchema.json`
                dbname = endpoint["dbname"]
                db = SqliteDatabase(self.logger, dbname)
                db.create_db_file()
                db.initialize_db()
                # Use the frequency defined by the user in the activationSchema.json
                db.frequency = endpoint["frequency"]
                # The schedule method can be used to set a method to be executed periodically.
                # In this case, its using the user-specified frequency, and will call the
                # `scheduled_query` method
                self.schedule(self.scheduled_query, timedelta(minutes=endpoint["frequency"]), (db,))
            except Exception:
                self.logger.warning(f"Could not connect to {dbname}")

    def scheduled_query(self, db):
        """
        This is the method that is scheduled to run, using the frequency set in the monitoring configuration.
        """
        self.logger.info(
            f"Running scheduled_query for {db.dbname}.db at interval of every {db.frequency} minute(s)"
        )
        try:
            # Get the host_name to pass as a dimension.
            db.socket_host = socket.gethostname()
            db_dims = {"database_name": db.dbname, "host_name": db.socket_host}
            report = db.report_db()
            self.logger.info(f"Report: {report}")
            rows = 0
            for result in report:
                for r in result:
                    db_dims.update({"table": r[0]})
                    rows = r[1]
                    # Report the metric key and dimensions that we want to send to Dynatrace.
                    self.report_metric(
                        key="python_vscode.example.sqlite.rows",
                        value=rows,
                        dimensions=db_dims,
                        metric_type=MetricType.GAUGE,
                    )
            # Since this extension is self contained to a SQLite database, this will cause the DB's row count
            # to increase so the metric values change.
            db.populate_db()
        except Exception as e:
            self.logger.error(f"Error connecting to {db.dbname}: {e}")
        self.logger.info(f"Completed scheduled_query method for {db.dbname}.db.")

    def fastcheck(self) -> Status:
        """
        Use to check if the extension can run.
        If this Activegate cannot run this extension, you can
        raise an Exception or return StatusValue.ERROR.
        This does not run for OneAgent extensions.
        """
        # Test if we can create an example SQLite .db file.
        # If a tempfile can be created, then the extension should run fine.
        test_db = SqliteDatabase(self.logger, "test")
        test_db.create_db_file()
        if test_db.db_file is not None:
            self.logger.info(f"Test db location is: {test_db.db_file}")
            # Return an OK status to Dynatrace.
            return Status(StatusValue.OK, "Fastcheck to test db successful.")
        # Return an ERROR status to Dynatrace.
        return Status(StatusValue.DEVICE_CONNECTION_ERROR, "Fastcheck to test db unsuccessful")


def main():
    ExtensionImpl(name="python-vscode-example").run()


if __name__ == "__main__":
    main()
