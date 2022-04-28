<?php declare( strict_types = 1);

require_once 'Exporter.php';

/**
 * TODO
 *
 * @author Malte Skoruppa <skoruppa@cs.uni-saarland.de>
 */
class GraphMLExporter extends Exporter {

  /** Default name of GraphML file */
  const GRAPHML_FILE = "graph.xml";

  /** Handle for the GraphML file */
  private $handle;

  /**
   * Constructor, creates file handlers.
   *
   * @param $outfile    Name of the GraphML output file
   * @param $startcount *Once* when creating the GraphMLExporter instance,
   *                    the starting node index may be chosen. Defaults to 0.
   */
  public function __construct( $outfile = self::GRAPHML_FILE, $startcount = 0) {

    $this->nodecount = $startcount;

    if( file_exists( $outfile))
      error_log( "[WARNING] $outfile already exists, overwriting it.");

    if( false === ($this->handle = fopen( $outfile, "w")))
      throw new IOError( "There was an error opening $outfile for writing.");

    // GraphML headers
    fwrite( $this->handle, '<?xml version="1.0" encoding="UTF-8"?>'."\n");
    fwrite( $this->handle, '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"'."\n");
    fwrite( $this->handle, '    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'."\n");
    fwrite( $this->handle, '    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns'."\n");
    fwrite( $this->handle, '     http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">'."\n");

    // node attributes
    // TODO not sure about the "label" key; it is supposed to be a "label" (key only) as opposed
    // to a "property" (key-value pair), but I do not know if GraphML has something like this
    fwrite( $this->handle, '  <key id="label" for="node" attr.name="label" attr.type="string"/>'."\n");
    fwrite( $this->handle, '  <key id="type" for="node" attr.name="type" attr.type="string"/>'."\n");
    // TODO a string array would be much better to represent a set of
    // flags, but arrays are not supported in GraphML
    fwrite( $this->handle, '  <key id="flags" for="node" attr.name="flags" attr.type="string"/>'."\n");
    fwrite( $this->handle, '  <key id="lineno" for="node" attr.name="lineno" attr.type="int"/>'."\n");
    fwrite( $this->handle, '  <key id="code" for="node" attr.name="code" attr.type="string"/>'."\n");
    fwrite( $this->handle, '  <key id="childnum" for="node" attr.name="childnum" attr.type="int"/>'."\n");
    fwrite( $this->handle, '  <key id="funcid" for="node" attr.name="funcid" attr.type="int"/>'."\n");
    fwrite( $this->handle, '  <key id="classname" for="node" attr.name="classname" attr.type="string"/>'."\n");
    fwrite( $this->handle, '  <key id="namespace" for="node" attr.name="namespace" attr.type="string"/>'."\n");
    fwrite( $this->handle, '  <key id="endlineno" for="node" attr.name="endlineno" attr.type="int"/>'."\n");
    fwrite( $this->handle, '  <key id="name" for="node" attr.name="name" attr.type="string"/>'."\n");
    fwrite( $this->handle, '  <key id="doccomment" for="node" attr.name="doccomment" attr.type="string"/>'."\n");

    // relationship attributes
    // NOTE: only in this case, the id is different from attr.name
    // This is because id's have to be globally unique, but we actually want a "type" property
    // on both edges and vertices; fortunately, for this purpose, it is the attr.type which matters
    fwrite( $this->handle, '  <key id="etype" for="edge" attr.name="type" attr.type="string"/>'."\n");

    // graph declaration
    fwrite( $this->handle, '  <graph id="G" edgedefault="directed">'."\n");
  }

  /**
   * Destructor, closes file handlers.
   */
  public function __destruct() {

    fwrite( $this->handle, '  </graph>'."\n");
    fwrite( $this->handle, '</graphml>'."\n");

    fclose( $this->handle);
  }

  /**
   * Implements the abstract function store_node() declared in the
   * Exporter class to export a node to a CSV file and increase the node
   * counter.
   */
  protected function store_node( $label, $type, $flags, $lineno, $code = null, $childnum = null, $funcid = null, $classname = null, $namespace = null, $endlineno = null, $name = null, $doccomment = null) : int {

    fwrite( $this->handle, '    <node id="'.$this->nodecount.'">'."\n");
    if( !($type === null || $type === "")) fwrite( $this->handle, '      <data key="label">'.$label.'</data>'."\n");
    if( !($type === null || $type === "")) fwrite( $this->handle, '      <data key="type">'.$type.'</data>'."\n");
    if( !($flags === null || $flags === "")) fwrite( $this->handle, '      <data key="flags">'.$flags.'</data>'."\n");
    if( !($lineno === null || $lineno === "")) fwrite( $this->handle, '      <data key="lineno">'.$lineno.'</data>'."\n");
    if( !($code === null || $code === "")) fwrite( $this->handle, '      <data key="code">'.$code.'</data>'."\n");
    if( !($childnum === null || $childnum === "")) fwrite( $this->handle, '      <data key="childnum">'.$childnum.'</data>'."\n");
    if( !($funcid === null || $funcid === "")) fwrite( $this->handle, '      <data key="funcid">'.$funcid.'</data>'."\n");
    if( !($classname === null || $classname === "")) fwrite( $this->handle, '      <data key="classname">'.$classname.'</data>'."\n");
    if( !($namespace === null || $namespace === "")) fwrite( $this->handle, '      <data key="namespace">'.$namespace.'</data>'."\n");
    if( !($endlineno === null || $endlineno === "")) fwrite( $this->handle, '      <data key="endlineno">'.$endlineno.'</data>'."\n");
    if( !($name === null || $name === "")) fwrite( $this->handle, '      <data key="name">'.$name.'</data>'."\n");
    if( !($doccomment === null || $doccomment === "")) fwrite( $this->handle, '      <data key="doccomment">'.$doccomment.'</data>'."\n");
    fwrite( $this->handle, '    </node>'."\n");

    // return the current node index, *then* increment it
    return $this->nodecount++;
  }

  /**
   * Implements the abstract function store_rel() declared in the
   * Exporter class to export a relationship to a CSV file.
   */
  public function store_rel( $start, $end, $type) {

    fwrite( $this->handle, '    <edge source="'.$start.'" target="'.$end.'">'."\n");
    fwrite( $this->handle, '      <data key="etype">'.$type.'</data>'."\n");
    fwrite( $this->handle, '    </edge>'."\n");
  }

  /**
   * Implements the abstract function quote_and_escape() declared
   * in the Exporter class.
   *
   * Replaces problematic signs in XML documents, namely
   * " -> &quot;
   * ' -> &apos;
   * < -> &lt;
   * > -> &gt;
   * & -> &amp;
   *
   * Also strips characters invalid in XML 1.0 documents:
   * basically, everything below \x20 except for \x9, \xA and \xD.

   * see http://stackoverflow.com/a/28152666
   *
   * Does not put quotes around the resulting string
   * (TODO rename this function into simply 'escape')
   */
  protected function quote_and_escape( $str) : string {

    // escape the character & first, so that if $str is, e.g.,
    // foo"bar, we don't end up with foo&amp;quot;bar (which would
    // happen if we escaped & last), but correctly with foo&quot;bar
    $str = str_replace( "&", "&amp;", $str);

    $str = str_replace( "\"", "&quot;", $str);
    $str = str_replace( "'", "&apos;", $str);
    $str = str_replace( "<", "&lt;", $str);
    $str = str_replace( ">", "&gt;", $str);

    // strip invalid characters
    $str = preg_replace( '/[\x0-\x8\xB\xC\xE-\x19]/', '', $str);
    // Note: Entity encoding would not be enough: we actually have to
    // strip these chars entirely, for they are simply not allowed in
    // XML documents. This is an inherent restriction and we cannot
    // get around it, lest we use XML 1.1. See:
    // http://stackoverflow.com/questions/5742543/an-invalid-xml-character-unicode-0xc-was-found#comment-6571610
    /*
    for( $i = 0; $i < 0x20; $i++) {
      if( $i === 0x9 || $i === 0xA || $i === 0xD) continue;
      $str = str_replace( chr($i), "&#{$i};", $str);
    }
    */

    return $str;
  }
}

