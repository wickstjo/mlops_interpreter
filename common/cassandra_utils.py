from cassandra.cluster import Cluster
import re

CASSANDRA_BROKERS = [('193.167.37.47', 12001)]
VERBOSE = False

########################################################################################################
########################################################################################################

class create_instance:
    def __init__(self, HIDE_LOGS=False):

        cluster = Cluster(CASSANDRA_BROKERS)
        self.instance = cluster.connect()

        if HIDE_LOGS:
            VERBOSE = False

    # def __del__(self):
        #self.instance.shutdown()

    ########################################################################################################
    ########################################################################################################

    # FREELY EXECUTE ANY CQL QUERY
    def query(self, query):
        try:
            return self.instance.execute(query)
        
        # SAFELY CATCH ERRORS
        except Exception as raw_error:
            parsed_error = self.parse_error(raw_error)
            raise Exception(f'[CASSANDRA] QUERY ERROR => {parsed_error}')

    ########################################################################################################
    ########################################################################################################
    
    # CASSANDRA DRIVER ERRORS ARE VERY MESSY
    # THIS ATTEMPT TO PARSE THEM TO MAKE EVERYTHING MORE HUMAN-READABLE
    def parse_error(self, error):
        stringified_error = str(error)
        
        # TRY TO REGEX MATCH THE ERROR PATTERN
        match = re.search(r'message="(.+)"', stringified_error)

        # MATCH FOUND, RETURN ISOLATED ERROR MSG
        if match:
            return match.group(1)
        
        # OTHERWISE, RETURN THE WHOLE THING
        return stringified_error
    
    ########################################################################################################
    ########################################################################################################

    # READ DATA FROM THE DATABASE
    def read(self, query: str, sort_by=False) -> list[dict]:
        try:
            container = []

            # PERFORM THE TABLE QUERY
            query_result = self.instance.execute(query)

            # PARSE EACH ROW AS A DICT
            for item in query_result:
                container.append(item._asdict())

            if VERBOSE: print(f'[CASSANDRA] READ {len(container)} FROM DATABASE')
            
            # SORT BY KEY WHEN REQUESTED
            if sort_by:
                return sorted(container, key=lambda x: x[sort_by])

            # OTHERWISE, RETURN UNSORTED
            return container
        
        # SAFELY CATCH ERRORS
        except Exception as raw_error:
            parsed_error = self.parse_error(raw_error)
            raise Exception(f'[CASSANDRA] READ ERROR => {parsed_error}')
    
    ########################################################################################################
    ########################################################################################################

    # COUNT TABLE ROWS -- SELECT COUNT(*) FROM ...
    def count(self, count_query: str) -> int:
        return int(self.read(count_query)[0]['count'])

    ########################################################################################################
    ########################################################################################################

    # FULL DATABASE OVERVIEW (KEYSPACES)
    def write(self, keyspace_table: str, row: dict):
        try:

            # SPLIT THE KEYS & VALUES
            columns = list(row.keys())
            values = list(row.values())

            # STITCH TOGETHER THE QUERY STRING
            query_string = f'INSERT INTO {keyspace_table} ('
            query_string += ', '.join(columns)
            query_string += ') values ('
            query_string += ', '.join(['?'] * len(columns))
            query_string += ');'
            
            # CONSTRUCT A PREPARED STATEMENT & EXECUTE THE DB WRITE
            prepared_statement = self.instance.prepare(query_string)
            self.instance.execute(prepared_statement, values)

            if VERBOSE: print('[CASSANDRA] WROTE TO DATABASE')
        
        # SAFELY CATCH ERRORS
        except Exception as raw_error:
            parsed_error = self.parse_error(raw_error)
            raise Exception(f'[CASSANDRA] WRITE ERROR => {parsed_error}')
        
    ########################################################################################################
    ########################################################################################################

    # CREATE A NEW KEYSPACE
    def create_keyspace(self, keyspace_name):
        try:
            self.instance.execute("""
                CREATE KEYSPACE IF NOT EXISTS %s WITH replication = {
                    'class': 'SimpleStrategy', 
                    'replication_factor': '1'
                };
            """ % keyspace_name).all()

        except Exception as raw_error:
            parsed_error = self.parse_error(raw_error)
            raise Exception(f'[CASSANDRA KEYSPACE ERROR] {parsed_error}')

    ########################################################################################################
    ########################################################################################################

    def create_table(self, keyspace_name, table_name, columns, indexing):
        try:

            # MAKE SURE PRIMARY KEYS ARE OK
            for key in indexing:
                col_list = list(columns.keys())
                
                if key not in col_list:
                    raise Exception(f"PRIMARY KEY '{key}' IS NOT A VALID COLUMN")
            
            # CREATE KEYSPACE IF NECESSARY
            self.create_keyspace(keyspace_name)

            # BASE QUERY
            query = f'CREATE TABLE {keyspace_name}.{table_name} ('
            
            # LOOP IN COLUMNS
            for column_name, column_type in columns.items():
                query += f'{column_name} {column_type}, '
                
            # ADD PRIMARY KEYS
            key_string = ', '.join(indexing)
            query += f'PRIMARY KEY({key_string}));'

            # CREATE THE TABLE
            self.instance.execute(query)

        except Exception as raw_error:
            parsed_error = self.parse_error(raw_error)
            raise Exception(f'[CASSANDRA CREATE ERROR] {parsed_error}')

    ########################################################################################################
    ########################################################################################################
 
    def drop_table(self, keyspace_name: str, table_name: str):
        try:
            self.instance.execute(f'DROP TABLE IF EXISTS {keyspace_name}.{table_name}')

        except Exception as raw_error:
            parsed_error = self.parse_error(raw_error)
            raise Exception(f'[CASSANDRA DROP ERROR] {parsed_error}')

    ########################################################################################################
    ########################################################################################################
