"""
Minimal Override for django-mssql to work with Azure Entra Authentication
Intercepts ALL connection methods to prevent Integrated Security
"""

from mssql.base import DatabaseWrapper as MSSQLDatabaseWrapper
import pyodbc


class DatabaseWrapper(MSSQLDatabaseWrapper):
    """
    Override ALL methods that might add Integrated Security
    """
    
    def get_connection_params(self):
        """Override to prevent parent from adding conflicting params"""
        # Return minimal params without letting parent add Integrated Security
        return {}
    
    def _get_new_connection(self, conn_params):
        """Override connection creation completely"""
        settings_dict = self.settings_dict
        
        # Build clean connection string without any parent interference
        conn_string = (
            f"DRIVER={{{settings_dict.get('OPTIONS', {}).get('driver', 'ODBC Driver 17 for SQL Server')}}};"
            f"SERVER={settings_dict.get('HOST')},{settings_dict.get('PORT', 1433)};"
            f"DATABASE={settings_dict.get('NAME')};"
            f"{settings_dict.get('OPTIONS', {}).get('extra_params', '')}"
        )
        
        print(f"🔗 Azure connection (bypassing parent): {conn_string}")
        
        try:
            connection = pyodbc.connect(conn_string)
            return connection
        except Exception as e:
            from django.db import DatabaseError
            raise DatabaseError(f"Azure SQL connection failed: {e}")
    
    def get_new_connection(self, conn_params):
        """Override the public method too"""
        return self._get_new_connection(conn_params)
