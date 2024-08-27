# YAMLsin
Tools to validate YAML file contents

A toolset to valid a YAML file. The files in genschema will generate a special schema file that encodes the requirements of the YANL file. The file in checker will take the generated schema file and some YAML file. The program will display all the "errors" generated in checking the YAML file against the scmema, of it will display Ok.

See the usage document in the docs subdirectory. The usage file is an Libre writer file, readable by evern office application I am familar with.

To generate the schema enter this command 

      cd genschema
      python main.py  -g -o <SCHEMA FILENAME>  <YAML FILE TO CHECK>

To check some YAML file against a generated schema, enter

    cd checker
    python cycle.py <YAML SCHEMA FILENAME>  <YAML FILE TO CHECK>



    
