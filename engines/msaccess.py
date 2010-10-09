import os
import platform
from dbtk.lib.models import Engine, no_cleanup

class engine(Engine):
    """Engine instance for Microsoft Access."""
    name = "Microsoft Access"
    abbreviation = "a"
    datatypes = ["AUTOINCREMENT",
                 "INTEGER",
                 "NUMERIC",
                 "NUMERIC",
                 "VARCHAR",
                 "BIT"]
    required_opts = [["file", 
                      "Enter the filename of your Access database: ",
                      "access.accdb",
                      "Access databases (*.mdb, *.accdb)|*.mdb;*.accdb"]]
    def convert_data_type(self, datatype):
        """MS Access can't handle complex Decimal types"""
        converted = Engine.convert_data_type(self, datatype)
        if "NUMERIC" in converted:
            converted = "NUMERIC"
        elif "VARCHAR" in converted:
            length = int(converted.split('(')[1].split(')')[0].split(',')[0])
            if length > 255:
                converted = "TEXT"
        return converted
    def create_db(self):
        """MS Access doesn't create databases."""
        return None
    def drop_statement(self, objecttype, objectname):
        """Returns a drop table or database SQL statement."""
        dropstatement = "DROP %s %s" % (objecttype, objectname)
        return dropstatement
    def format_column_name(self, column):
        return "[" + str(column) + "]"
    def insert_data_from_file(self, filename):
        """Perform a bulk insert."""
        if (self.table.cleanup.function == no_cleanup and 
            self.table.header_rows < 2) and (self.table.delimiter in ["\t", ","]):        
            print ("Inserting data from " + os.path.basename(filename) 
                   + " . . .")
            
            if self.table.delimiter == "\t":
                fmt = "TabDelimited"
            elif self.table.delimiter == ",":
                fmt = "CSVDelimited"
                
            if self.table.header_rows == 1:
                hdr = "Yes"
            else:
                hdr = "No"
            
            need_to_delete = False    
            if self.table.pk and not self.table.hasindex:
                newfilename = '.'.join(filename.split(".")[0:-1]) + "_new." + filename.split(".")[-1]
                if not os.path.isfile(newfilename):
                    print "Adding index to " + os.path.abspath(newfilename) + " . . ."
                    read = open(filename, "rb")
                    write = open(newfilename, "wb")            
                    id = self.table.record_id
                    for line in read:
                        write.write(str(id) + self.table.delimiter + line)
                        id += 1
                    self.table.record_id = id
                    write.close()
                    read.close()
                    need_to_delete = True
            else:
                newfilename = filename
            
            columns = self.get_insert_columns()
            filename = os.path.abspath(newfilename)
            filename_length = (len(os.path.basename(filename)) * -1) - 1
            filepath = filename[0:filename_length]
            statement = """
INSERT INTO """ + self.tablename() + " (" + columns + """)
SELECT * FROM [""" + os.path.basename(filename) + ''']
IN "''' + filepath + '''" "Text;FMT=''' + fmt + ''';HDR=''' + hdr + ''';"'''
            
            try:
                self.cursor.execute(statement)
                self.connection.commit()
            except:
                raise
                exit()
                self.connection.rollback()                
                return Engine.insert_data_from_file(self, filename)
            
            if need_to_delete:
                os.remove(newfilename)
        else:
            return Engine.insert_data_from_file(self, filename)    
    def tablename(self):
        return "[" + self.db.dbname + " " + self.table.tablename + "]"
    def get_cursor(self):
        """Gets the db connection and cursor."""
        if not "win" in platform.platform().lower():
            raise Exception("MS Access can only be used in Windows.")
        import pyodbc as dbapi
        self.get_input()
        connection_string = ("DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ="
                             + self.opts["file"].replace("/", "//") + ";")
        self.connection = dbapi.connect(connection_string,
                                        autocommit = False)
        self.cursor = self.connection.cursor()


def choose_engine(opts):
    """Prompts the user to select a database engine"""    
    if "engine" in opts.keys():
        enginename = opts["engine"]    
    else:
        print "Choose a database engine:"
        for engine in ALL_ENGINES:
            if engine.abbreviation:
                abbreviation = "(" + engine.abbreviation + ") "
            else:
                abbreviation = ""
            print "    " + abbreviation + engine.name
        enginename = raw_input(": ")
        enginename = enginename.lower()
    
    engine = Engine()
    if not enginename:
        engine = MySQLEngine()
    else:
        for thisengine in ALL_ENGINES:
            if (enginename == thisengine.name.lower() 
                              or thisengine.abbreviation
                              and enginename == thisengine.abbreviation):
                engine = thisengine
        
    engine.opts = opts
    return engine
