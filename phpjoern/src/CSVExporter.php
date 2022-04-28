<?php declare( strict_types = 1);

require_once 'Exporter.php';

/**
 * This class exports ASTs into two CSV files, one for nodes and one
 * for edges. The concrete syntax for these CSV files comes in two
 * different flavors, both of which are supported by this class: One
 * is used by the tool batch-import
 * (https://github.com/jexp/batch-import, by Michael Hunger), while
 * the other is used by the tool neo4j-import that comes bundled with
 * Neo4J since version 2.2. Both of these tools are designed to import
 * CSV files into a Neo4J database.
 *
 * @author Malte Skoruppa <skoruppa@cs.uni-saarland.de>
 */
class CSVExporter extends Exporter {

  /** Used format -- defaults to Neo4J */
  private $format = self::NEO4J_FORMAT;

  /** Delimiter for columns in CSV files */
  private $csv_delim = ",";

  /** Default name of node file */
  const NODE_FILE = "nodes.csv";
  /** Default name of relationship file */
  const REL_FILE = "rels.csv";

  /** Handle for the node file */
  private $nhandle;
  /** Handle for the relationship file */
  private $rhandle;

  /**
   * Constructor, creates file handlers.
   *
   * @param $format     Format to use for export (neo4j or jexp)
   * @param $nodefile   Name of the nodes file
   * @param $relfile    Name of the relationships file
   * @param $startcount *Once* when creating the CSVExporter instance,
   *                    the starting node index may be chosen. Defaults to 0.
   */
  public function __construct( $format = self::NEO4J_FORMAT, $nodefile = self::NODE_FILE, $relfile = self::REL_FILE, $startcount = 0) {

    $this->format = $format;
    $this->nodecount = $startcount;

    foreach( [$nodefile, $relfile] as $file)
      if( file_exists( $file))
        error_log( "[WARNING] $file already exists, overwriting it.");

    if( false === ($this->nhandle = fopen( $nodefile, "w")))
      throw new IOError( "There was an error opening $nodefile for writing.");
    if( false === ($this->rhandle = fopen( $relfile, "w")))
      throw new IOError( "There was an error opening $relfile for writing.");

    // if format is non-default, adapt delimiters and headers
    if( $this->format === self::JEXP_FORMAT) {
      $this->csv_delim = "\t";
      $this->array_delim = ",";

      fwrite( $this->nhandle, "id:int{$this->csv_delim}labels:label{$this->csv_delim}type{$this->csv_delim}flags:string_array{$this->csv_delim}lineno:int{$this->csv_delim}code{$this->csv_delim}childnum:int{$this->csv_delim}funcid:int{$this->csv_delim}classname{$this->csv_delim}namespace{$this->csv_delim}endlineno:int{$this->csv_delim}name{$this->csv_delim}doccomment\n");
      fwrite( $this->rhandle, "start{$this->csv_delim}end{$this->csv_delim}type\n");
    }
    else {
      fwrite( $this->nhandle, "id:ID{$this->csv_delim}:LABEL{$this->csv_delim}type{$this->csv_delim}flags:string[]{$this->csv_delim}lineno:int{$this->csv_delim}code{$this->csv_delim}childnum:int{$this->csv_delim}funcid:int{$this->csv_delim}classname{$this->csv_delim}namespace{$this->csv_delim}endlineno:int{$this->csv_delim}name{$this->csv_delim}doccomment\n");
      fwrite( $this->rhandle, ":START_ID{$this->csv_delim}:END_ID{$this->csv_delim}:TYPE\n");
    }
  }

  /**
   * Destructor, closes file handlers.
   */
  public function __destruct() {

    fclose( $this->nhandle);
    fclose( $this->rhandle);
  }

  /**
   * Implements the abstract function store_node() declared in the
   * Exporter class to export a node to a CSV file and increase the node
   * counter.
   */
  protected function store_node( $label, $type, $flags, $lineno, $code = null, $childnum = null, $funcid = null, $classname = null, $namespace = null, $endlineno = null, $name = null, $doccomment = null) : int {

    fwrite( $this->nhandle, "{$this->nodecount}{$this->csv_delim}{$label}{$this->csv_delim}{$type}{$this->csv_delim}{$flags}{$this->csv_delim}{$lineno}{$this->csv_delim}{$code}{$this->csv_delim}{$childnum}{$this->csv_delim}{$funcid}{$this->csv_delim}{$classname}{$this->csv_delim}{$namespace}{$this->csv_delim}{$endlineno}{$this->csv_delim}{$name}{$this->csv_delim}{$doccomment}\n");

    // return the current node index, *then* increment it
    return $this->nodecount++;
  }

  /**
   * Implements the abstract function store_rel() declared in the
   * Exporter class to export a relationship to a CSV file.
   */
  public function store_rel( $start, $end, $type) {

    fwrite( $this->rhandle, "{$start}{$this->csv_delim}{$end}{$this->csv_delim}{$type}\n");
  }

  /**
   * Implements the abstract function quote_and_escape() declared
   * in the Exporter class.
   *
   * Replaces ambiguous signs in $str, namely
   * \ -> \\
   * " -> \"
   * TODO because of a bug in neo4j-import, we also
   * replace newlines for now:
   * \n -> \\n
   * \r -> \\r
   * Additionally, puts quotes around the resulting string.
   */
  protected function quote_and_escape( $str) : string {

    $str = str_replace( "\\", "\\\\", $str);

    // let's escape newlines to avoid problems when parsing the CSV files
    $str = str_replace( "\n", "\\n", $str);
    $str = str_replace( "\r", "\\r", $str);

    $str = "\"".str_replace( "\"", "\\\"", $str)."\"";

    return $str;
  }
}

