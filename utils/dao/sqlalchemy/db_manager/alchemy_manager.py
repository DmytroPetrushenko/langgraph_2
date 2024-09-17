import logging

from datetime import datetime
from sqlalchemy import create_engine, inspect, Engine, Row, RowMapping, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, DeclarativeMeta
from typing import Type, Sequence, Any, List, Optional

from utils.dao.sqlalchemy.models import ModuleAuxiliary, ModuleOptionsAuxiliary, DynamicConsoleResult, Base


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManagerAlchemyDB:
    """
    Database manager class for handling SQLAlchemy operations.
    """

    def __init__(self, db_url: str):
        """
        Initialize the ManagerDB with a database URL.

        :param db_url: SQLAlchemy database URL
        """
        self._engine: Engine = create_engine(db_url, echo=True, future=True)
        self._Session = sessionmaker(self._engine)

    def create_tables_by_models(self, base: Type[DeclarativeMeta]) -> None:
        """
        Create database tables based on the provided SQLAlchemy models.

        :param base: DeclarativeMeta instance containing model definitions
        """
        try:
            base.metadata.create_all(self._engine)
            logger.info("Tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")

    def get_sub_group_from_module_auxiliary(self) -> Sequence[Row[Any] | RowMapping | Any] | list[Any]:
        """
        Fetch unique 'sub_group' values from the ModuleAuxiliary table.

        :return: List of unique 'sub_group' values
        """
        try:
            with self._Session() as session:
                result = session.execute(
                    select(ModuleAuxiliary.sub_group).distinct()
                ).scalars().all()
                return result
        except SQLAlchemyError as e:
            logger.error(f"Error fetching sub_group values: {e}")
            return []

    def get_modules_by_sub_group_list_from_module_auxiliary(
            self,
            sub_group_name: str
    ) -> Sequence[Row[Any] | RowMapping | Any] | list[Any]:
        """
        Retrieve modules by their 'sub_group' from the ModuleAuxiliary table.

        :param sub_group_name: The name of the sub_group to filter modules by
        :return: List of tuples containing module names and descriptions
        """
        try:
            with self._Session() as session:
                return session.execute(
                    select(ModuleAuxiliary.name, ModuleAuxiliary.description).
                    where(ModuleAuxiliary.sub_group.is_(sub_group_name))
                ).scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching modules for sub_group '{sub_group_name}': {e}")
            return []

    def get_module_options(self, module_name: str) -> List[Optional[str]]:
        """
        Retrieve all non-null parameter fields for a given module.

        :param module_name: The name of the module to retrieve options for
        :return: List of non-null parameter values
        """
        try:
            fields = [getattr(ModuleOptionsAuxiliary, f"parameter_{i}") for i in range(1, 20)]
            with self._Session() as session:
                result = session.execute(
                    select(*fields).where(ModuleOptionsAuxiliary.module_name == module_name)
                ).first()
                return [value for value in result if value is not None] if result else []
        except SQLAlchemyError as e:
            logger.error(f"Error fetching options for module '{module_name}': {e}")
            return []


    def write_to_db(self, host: str, module: str, output: str, compressed_output: str) -> None:
        """
        Write console output to a dynamically named table.

        :param host: The host information
        :param module: The module name
        :param output: The console output to be stored
        :param compressed_output: Compressed console output
        """
        try:
            with self._Session() as session:
                # Generate the dynamic table name
                table_name = get_table_name()

                # Dynamically create the model class with the table name
                class ScanResult(DynamicConsoleResult):
                    __tablename__ = table_name
                    __table_args__ = {'extend_existing': True}

                # Check if the table exists, and create it if it doesn't
                inspector = inspect(self._engine)
                if not inspector.has_table(ScanResult.__tablename__):
                    Base.metadata.create_all(self._engine, tables=[ScanResult.__table__])

                # Create a new record
                new_result = ScanResult(
                    host=host,
                    module=module,
                    output=output,
                    compressed_output=compressed_output
                )

                session.add(new_result)
                session.commit()
                logger.info(f"Data successfully written to {ScanResult.__tablename__}")
        except SQLAlchemyError as e:
            logger.error(f"Error writing to database: {e}")


def get_table_name() -> str:
    """Generate a table name based on the current date."""
    current_date = datetime.now().strftime("%Y_%m_%d")
    return f"msf_console_{current_date}"
