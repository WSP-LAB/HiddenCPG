<?php declare( strict_types = 1);

// report on errors, except notices
error_reporting( E_ALL & ~E_NOTICE);

/**
 * This program looks for PHP files in a given directory and dumps ASTs.
 *
 * @author Malte Skoruppa <skoruppa@cs.uni-saarland.de>
 */

require_once 'Exporter.php';
require_once 'CSVExporter.php';
require_once 'GraphMLExporter.php';

$path = null; // file/folder to be parsed
$format = Exporter::JEXP_FORMAT; // format to use for export (default: jexp)
$nodefile = CSVExporter::NODE_FILE; // name of node file when using CSV format (default: nodes.csv)
$relfile = CSVExporter::REL_FILE; // name of relationship file when using CSV format (default: rels.csv)
$outfile = GraphMLExporter::GRAPHML_FILE; // name of output file when using GraphML format (default: graph.xml)
$scriptname = null; // this script's name
$startcount = 0; // the start count for numbering nodes

/**
 * Parses the cli arguments.
 *
 * @return Boolean that indicates whether the given arguments are
 *         fine.
 */
function parse_arguments() {

  global $argv;
  
  if( !isset( $argv)) {
    if( false === (boolean) ini_get( 'register_argc_argv')) {
      error_log( '[ERROR] Please enable register_argc_argv in your php.ini.');
    }
    else {
      error_log( '[ERROR] No $argv array available.');
    }
    echo PHP_EOL;
    return false;
  }

  // Remove the script name (first argument)
  global $scriptname;
  $scriptname = array_shift( $argv);

  if( count( $argv) === 0) {
    error_log( '[ERROR] Missing argument.');
    return false;
  }

  // Set the path and remove from command line (last argument)
  global $path;
  $path = (string) array_pop( $argv);

  // Parse options
  $longopts  = ["help", "version", "format:", "nodes:", "relationships:", "out:", "count:"];
  $options = getopt( "hvf:n:r:o:c:", $longopts);
  if( $options === FALSE) {
    error_log( '[ERROR] Could not parse command line arguments.');
    return false;
  }

  // Help?
  if( isset( $options['help']) || isset( $options['h'])) {
    print_version();
    echo PHP_EOL;
    print_usage();
    echo PHP_EOL;
    print_help();
    exit( 0);
  }

  // Version?
  if( isset( $options['version']) || isset( $options['v'])) {
    print_version();
    exit( 0);
  }

  // Format?
  if( isset( $options['format']) || isset( $options['f'])) {
    global $format;
    switch( $options['format'] ?? $options['f']) {
    case "jexp":
      $format = Exporter::JEXP_FORMAT;
      break;
    case "neo4j":
      $format = Exporter::NEO4J_FORMAT;
      break;
    case "graphml":
      $format = Exporter::GRAPHML_FORMAT;
      break;
    default:
      error_log( "[WARNING] Unknown format '{$options['f']}', using jexp format.");
      $format = Exporter::JEXP_FORMAT;
      break;
    }
  }

  // Nodes file? (for CSV output)
  if( isset( $options['nodes']) || isset( $options['n'])) {
    global $nodefile;
    $nodefile = $options['nodes'] ?? $options['n'];
  }

  // Relationships file? (for CSV output)
  if( isset( $options['relationships']) || isset( $options['r'])) {
    global $relfile;
    $relfile = $options['relationships'] ?? $options['r'];
  }

  // Output file? (for XML output)
  if( isset( $options['out']) || isset( $options['o'])) {
    global $outfile;
    $outfile = $options['out'] ?? $options['o'];
  }

  // Start count?
  if( isset( $options['count']) || isset( $options['c'])) {
    global $startcount;
    $startcount = (int)($options['count'] ?? $options['c']);
  }

  return true;
}

/**
 * Prints a version message.
 */
function print_version() {

  $version = 'UNKNOWN';

  // Note: Only works on Unix :-p
  if( file_exists( ".git/HEAD"))
    if( preg_match( '/^ref: (.+)$/', file_get_contents( ".git/HEAD"), $matches))
      if( file_exists( ".git/{$matches[1]}"))
        $version = substr( file_get_contents( ".git/{$matches[1]}"), 0, 7);

  echo "PHPJoern parser utility, commit {$version}", PHP_EOL;
}

/**
 * Prints a usage message.
 */
function print_usage() {

  global $scriptname;
  echo 'Usage: php '.$scriptname.' [options] <file|folder>', PHP_EOL;
}

/**
 * Prints a help message.
 */
function print_help() {

  echo 'Options:', PHP_EOL;
  echo '  -h, --help                 Display help message', PHP_EOL;
  echo '  -v, --version              Display version information', PHP_EOL;
  echo '  -f, --format <format>      Format to use for the output files: "jexp" (default), "neo4j", or "graphml"', PHP_EOL;
  echo '  -n, --nodes <file>         Output file for nodes (for CSV output, i.e., neo4j or jexp modes)', PHP_EOL;
  echo '  -r, --relationships <file> Output file for relationships (for CSV output, i.e., jexp or neo4j modes)', PHP_EOL;
  echo '  -o, --out <file>           Output file for entire graph (for XML output, i.e., graphml mode)', PHP_EOL;
  echo '  -c, --count <number>       Initial value of node counter (defaults to 0)', PHP_EOL;
}

/**
 * Parses and generates an AST for a single file.
 *
 * @param $path     Path to the file
 * @param $exporter An Exporter instance to use for exporting
 *                  the AST of the parsed file.
 *
 * @return The node index of the exported file node, or -1 if there
 *         was an error.
 */
function parse_file( $path, $exporter) : int {

  $finfo = new SplFileInfo( $path);
  echo "Parsing file ", $finfo->getPathname(), PHP_EOL;

  try {
    $ast = ast\parse_file( $path, $version = 35);

    // The above may throw a ParseError. We only export to the output
    // file(s) if that didn't happen.
    $fnode = $exporter->store_filenode( $finfo->getFilename());
    $tnode = $exporter->store_toplevelnode( Exporter::TOPLEVEL_FILE, $path, 1, count(file($path)));
    $astroot = $exporter->export( $ast, $tnode);
    $exporter->store_rel( $tnode, $astroot, "PARENT_OF");
    $exporter->store_rel( $fnode, $tnode, "FILE_OF");
    //echo ast_dump( $ast), PHP_EOL;
  }
  catch( ParseError $e) {
    $fnode = -1;
    error_log( "[ERROR] In $path: ".$e->getMessage());
  }

  return $fnode;
}

/**
 * Parses and generates ASTs for all PHP files buried within a
 * directory.
 *
 * @param $path     Path to the directory
 * @param $exporter An Exporter instance to use for exporting
 *                  the ASTs of all parsed files.
 * @param $top      Boolean indicating whether this call
 *                  corresponds to the top-level call of the
 *                  function. We wouldn't need this if I didn't
 *                  insist on the root directory of a project
 *                  getting node index 0. But, I do insist.
 *
 * @return If the directory corresponding to the function call finds
 *         itself interesting, it stores a directory node for itself
 *         and this function returns the index of that
 *         node. Otherwise, returns -1. A directory finds itself
 *         interesting if it contains PHP files, or if one of its
 *         child directories finds itself interesting. -- As a special
 *         case, the root directory of a project (corresponding to the
 *         top-level call) always finds itself interesting and always
 *         stores a directory node for itself.
 */
function parse_dir( $path, $exporter, $top = true) : int {

  // save any interesting directory/file indices in the current folder
  $found = [];
  // if the current folder finds itself interesting, we will create a
  // directory node for it and return its index
  $dirnode = $top ? $exporter->store_dirnode( basename( $path)) : -1;

  $dhandle = opendir( $path);

  // iterate over everything in the current folder
  while( false !== ($filename = readdir( $dhandle))) {
    $finfo = new SplFileInfo( build_path( $path, $filename));

    if( $finfo->isFile() && $finfo->isReadable() && in_array( strtolower( $finfo->getExtension()), ['php','inc','phar']))
      $found[] = parse_file( $finfo->getPathname(), $exporter);
    else if( $finfo->isDir() && $finfo->isReadable() && $filename !== '.' && $filename !== '..')
      if( -1 !== ($childdir = parse_dir( $finfo->getPathname(), $exporter, false)))
        $found[] = $childdir;
  }

  // if the current folder finds itself interesting...
  if( !empty( $found)) {
    if( !$top)
      $dirnode = $exporter->store_dirnode( basename( $path));
    foreach( $found as $i => $nodeindex)
      $exporter->store_rel( $dirnode, $nodeindex, "DIRECTORY_OF");
  }

  closedir( $dhandle);

  return $dirnode;
}

/**
 * Builds a file path with the appropriate directory separator.
 *
 * @param ...$segments Unlimited number of path segments.
 *
 * @return The file path built from the path segments.
 */
function build_path( ...$segments) {

  return join( DIRECTORY_SEPARATOR, $segments);
}

/*
 * Main script
 */
if( parse_arguments() === false) {
  print_usage();
  echo PHP_EOL;
  print_help();
  exit( 1);
}

// Check that source exists and is readable
if( !file_exists( $path) || !is_readable( $path)) {
  error_log( '[ERROR] The given path does not exist or cannot be read.');
  exit( 1);
}

$exporter = null;
// Determine whether source is a file or a directory
if( is_file( $path)) {
  try {
    if( $format === Exporter::GRAPHML_FORMAT)
      $exporter = new GraphMLExporter( $outfile, $startcount);
    else // either NEO4J_FORMAT or JEXP_FORMAT
      $exporter = new CSVExporter( $format, $nodefile, $relfile, $startcount);
  }
  catch( IOError $e) {
    error_log( "[ERROR] ".$e->getMessage());
    exit( 1);
  }
  parse_file( $path, $exporter);
}
elseif( is_dir( $path)) {
  try {
    if( $format === Exporter::GRAPHML_FORMAT)
      $exporter = new GraphMLExporter( $outfile, $startcount);
    else // either NEO4J_FORMAT or JEXP_FORMAT
      $exporter = new CSVExporter( $format, $nodefile, $relfile, $startcount);
  }
  catch( IOError $e) {
    error_log( "[ERROR] ".$e->getMessage());
    exit( 1);
  }
  parse_dir( $path, $exporter);
}
else {
  error_log( '[ERROR] The given path is neither a regular file nor a directory.');
  exit( 1);
}

echo "Done.", PHP_EOL;
