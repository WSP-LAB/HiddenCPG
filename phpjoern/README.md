This is the phpjoern utility for Joern. It uses the `php-ast` extension
to generate ASTs from PHP projects and exports these to CSV files
suitable to be parsed by Joern.

More information on Joern and PHP may be found in our paper
[Efficient and Flexible Discovery of PHP Application Vulnerabilities](https://www.infsec.cs.uni-saarland.de/~skoruppa/publications/skoruppa_eurosp2017.pdf)
published at EuroS&P 2017.

# Prerequisite: Installing the php-ast extension

First off, you need a working installation of PHP 7.2. Next, you need to
set up the `php-ast` extension, available at:

[https://github.com/nikic/php-ast](https://github.com/nikic/php-ast)

Essentially, clone the repository, then compile and install the
extension as follows:

    git clone https://github.com/nikic/php-ast
    git checkout v0.1.2
    phpize
    ./configure
    make
    sudo make install
	
Lastly, add the line `extension=ast.so` to your `php.ini` file.

# Using the parser

The parser is implemented in PHP and makes use of the `php-ast` extension.
A simple Bash wrapper script in the repository's root directory called
`php2ast` serves as an entry point. It takes the path to a PHP file or to
a directory as an argument. If the provided argument is a directory, the
parser will recursively search for all PHP files in that directory and
generate an AST for each of them.

Before executing the script, the environment variable `$PHP7` should be
set to the location of the `php` executable of PHP 7. If no such variable
is set, the location `/usr/bin/php` will be used by default.

Example usage:

    ./php2ast somefile.php
    ./php2ast somedirectory/

Either of these calls will generate two CSV files `nodes.csv` and `rels.csv`
representing the nodes of the generated AST(s) and their relationships,
respectively. In addition, directory and file nodes are also created and
connected to the individual AST root nodes to reflect a scanned directory's
structure and obtain a single large tree.

By default, the specific format of the CSV files is the format required by
the `batch-import` tool for Neo4J (see below), available at:

[https://github.com/jexp/batch-import](https://github.com/jexp/batch-import)

Other output formats are supported, such as
[Neo4J's own CSV format](https://neo4j.com/developer/guide-import-csv/#_super_fast_batch_importer_for_huge_datasets)
and [GraphML](http://graphml.graphdrawing.org). See

    ./php2ast --help

for help. However, note that Joern currently only supports the default format
as an input format. In addition, Joern outputs code property graph edges
only in this same format, although additional output modules should be
easy to implement.

# Generating code property graphs with Joern

The CSV files generated in the previous step can now be passed to Joern.
Joern will read these files, analyze the ASTs, generate control flow
and program dependence edges for them, and output the calculated edges in
another CSV file. First off, obtain Joern here:

[https://github.com/octopus-platform/joern](https://github.com/octopus-platform/joern)

Essentially, clone the repository and build the project:

    git clone https://github.com/octopus-platform/joern
    gradle build

In Joern's root directory, there is a small Bash wrapper script that serves
as an entry point for generating code property graphs for PHP, called
`phpast2cpg`. It takes two arguments: The node files and the edges file
generated in the previous step, in that order. Use it as follows:

    ./phpast2cpg nodes.csv rels.csv
	
Joern will then output a file `cpg_edges.csv`, representing the calculated
control flow and program dependence edges.

# Importing the code property graphs into Neo4J

You should now have three CSV files, named `nodes.csv`, `rels.csv` and
`cpg_edges.csv` by default. These files can be used to create a Neo4J
database using the tool [batch-import](https://github.com/jexp/batch-import).

It is easiest to download a precompiled `batch-import` for the particular
Neo4J version you intend to use. For instance, for Neo4J 2.1:

    mkdir batch-import
    cd batch-import
    curl -O https://dl.dropboxusercontent.com/u/14493611/batch_importer_21.zip
    unzip batch_importer_21.zip

In the following, let let `$JEXP_HOME` be the absolute path to the newly
created directory `batch-import/`, and `$PHPJOERN_HOME` the absolute path
to your installation of the present repository.

To import the generated CSV files into a Joern Neo4J database,
simply use the following:

    java -classpath "$JEXP_HOME/lib/*" -Dfile.encoding=UTF-8 org.neo4j.batchimport.Importer $PHPJOERN_HOME/conf/batch.properties graph.db nodes.csv rels.csv,cpg_edges.csv

The performance you experience will mainly depend on the heap size that you
allocate. You should edit the file `$PHPJOERN_HOME/conf/batch.properties`
accordingly, see [here](http://joern.readthedocs.io/en/latest/performance.html#optimizing-code-importing).
The `batch.properties` file that comes with `phpjoern` is optimized for heap
sizes larger than 4 GB that you should allocate accordingly, e.g.,

    HEAP=6G
    java -classpath "$JEXP_HOME/lib/*" -Xmx$HEAP -Xms$HEAP -Dfile.encoding=UTF-8 org.neo4j.batchimport.Importer conf/batch.properties graph.db nodes.csv rels.csv

Once the import is finished, you will have a directory `graph.db` suitable for Neo4J.
You may now point your Neo4J installation to that database and start your analysis.

For further discussion, refer to [http://joern.readthedocs.io.](http://joern.readthedocs.io.)
