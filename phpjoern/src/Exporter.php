<?php declare( strict_types = 1);

// needed for the flag constants -- i.e., essentially get_flag_info()
// used in format_flags()
require_once 'util.php';

/**
 * This abstract class defines the various methods implemented by its
 * inheriting classes used to export ASTs into various formats. It
 * also implements those methods that are common to all its inheriting
 * classes.
 *
 * @author Malte Skoruppa <skoruppa@cs.uni-saarland.de>
 */
abstract class Exporter {

  /** Node counter */
  protected $nodecount = 0;

  /** Constant for Neo4J format (to be used with neo4j-import) */
  const NEO4J_FORMAT = 0;
  /** Constant for jexp format (to be used with batch-import) */
  const JEXP_FORMAT = 1;
  /** Constant for GraphML format (supported by many tools) */
  const GRAPHML_FORMAT = 2;

  /** Labels */
  const LABEL_FS = "Filesystem";
  const LABEL_AST = "AST";
  const LABEL_ART = "Artificial";

  /** Type of directory nodes */
  const DIR = "Directory";
  /** Type of file nodes */
  const FILE = "File";
  /** Type of toplevel nodes */
  const TOPLEVEL = "AST_TOPLEVEL";
  /** Flags for toplevel nodes */
  const TOPLEVEL_FILE = "TOPLEVEL_FILE";
  const TOPLEVEL_CLASS = "TOPLEVEL_CLASS";

  /** Type of entry and exit nodes (for CFG construction) */
  const FUNC_ENTRY = "CFG_FUNC_ENTRY";
  const FUNC_EXIT = "CFG_FUNC_EXIT";

  /** Delimiter for arrays, used by format_flags() */
  protected $array_delim = ";";

  /**
   * Exports a syntax tree by recursing through the tree and calling
   * the functions store_node() and store_rel() appropriately.
   *
   * @param $ast       The AST to export.
   * @param $funcid    The node id of the function that this AST belongs
   *                   to. This must always be defined, since we also
   *                   declare "fake" toplevel function nodes for files
   *                   and for classes.
   * @param $nodeline  Indicates the nodeline of the parent node. This
   *                   is necessary when $ast is a plain value, since
   *                   we cannot get back from a plain value to the
   *                   parent node to learn the line number.
   * @param $childname Indicates that this node is the $childname child
   *                   of its parent node.
   *                   See: https://github.com/nikic/php-ast/issues/12
   * @param $childnum  Indicates that this node is the $childnum'th
   *                   child of its parent node (starting at 0).
   * @param $namespace The current namespace of the node.
   * @param $uses      An array of translation rules representing the
   *                   imported namespaces (e.g., ["C" => "A\B\C"]). The
   *                   translation rules will be applied to all AST_NAME
   *                   nodes during export of the AST.
   * @param $classname The class name of the class that this AST belongs
   *                   to, if any.
   * 
   * @return The root node index of the exported AST (i.e., the value
   *         of $this->nodecount at the point in time where this
   *         function was called.)
   */
  public function export( $ast, $funcid, $nodeline = 0, $childname = "", $childnum = 0, $namespace = "", $uses = [], $classname = "") : int {
      
    // (1) if $ast is an AST node, print info and recurse
    // An instance of ast\Node declares:
    // $kind (integer, name can be retrieved using ast\get_kind_name())
    // $flags (integer, corresponding to a set of flags for the current node)
    // $lineno (integer, starting line number)
    // $children (array of child nodes)
    // Additionally, an instance of the subclass ast\Node\Decl declares:
    // $endLineno (integer, end line number of the declaration)
    // $name (string, the name of the declared function/class)
    // $docComment (string, the preceding doc comment)
    if( $ast instanceof ast\Node) {

      $nodetype = ast\get_kind_name( $ast->kind);
      $nodeline = $ast->lineno;

      $nodeflags = "";
      if( ast\kind_uses_flags( $ast->kind)) {
        $nodeflags = $this->format_flags( $ast->kind, $ast->flags);
      }

      // for decl nodes:
      if( isset( $ast->endLineno)) {
        $nodeendline = $ast->endLineno;
      }
      if( isset( $ast->name)) {
        $nodename = $ast->name;
      }
      if( isset( $ast->docComment)) {
        $nodedoccomment = $this->quote_and_escape( $ast->docComment);
      }
      
      // store node, export all children and store the relationships
      $rootnode = $this->store_node( self::LABEL_AST, $nodetype, $nodeflags, $nodeline, null, $childnum, $funcid, $classname, $this->quote_and_escape( $namespace), $nodeendline, $nodename, $nodedoccomment);

      // If this node is a function/method/closure declaration, set $funcid.
      // Note that in particular, the decl node *itself* does not have $funcid set to its own id;
      // this is intentional. The *declaration* of a function/method/closure itself is part of the
      // control flow of the outer scope: e.g., a closure declaration is part of the control flow
      // of the function it is declared in, or a function/method declaration is part of the control flow
      // of the pseudo-function representing the top-level code it is declared in.
      // Note: we do not need to do this for TOPLEVEL types (and it wouldn't be straightforward since we
      // do not generate ast\Node objects for them). Rather, for toplevel nodes under files, the funcid is
      // set by the Parser class, which also stores the File node; and for toplevel nodes under classes,
      // we do it below, while iterating over the children.
      // Also, we create artificial entry and exit nodes for the CFG of the function (like file and dir nodes,
      // they are not actually part of the AST).
      // For the entry and exit nodes, we only set
      // (1) the funcid (to the id of the function node), and
      // (2) the name (to that of the function)
      if( $ast->kind === ast\AST_FUNC_DECL || $ast->kind === ast\AST_METHOD || $ast->kind === ast\AST_CLOSURE) {
        $funcid = $rootnode;
        $entrynode = $this->store_node( self::LABEL_ART, self::FUNC_ENTRY, null, null, null, null, $rootnode, $classname, $this->quote_and_escape( $namespace), null, $this->quote_and_escape( $nodename), null);
        $exitnode = $this->store_node( self::LABEL_ART, self::FUNC_EXIT, null, null, null, null, $rootnode, $classname, $this->quote_and_escape( $namespace), null, $this->quote_and_escape( $nodename), null);
        $this->store_rel( $rootnode, $entrynode, "ENTRY");
        $this->store_rel( $rootnode, $exitnode, "EXIT");
      }

      // If this node is a class declaration, set $classname
      if( $ast->kind === ast\AST_CLASS) {
        $classname = $nodename;
      }

      // iterate over the children and count them
      $i = 0;
      foreach( $ast->children as $childrel => $child) {

        // If we encounter a child node that is a namespace node, set the namespace for subtrees and upcoming sister nodes
        // Note that we do not care whether the non-bracketed syntax (second child of AST_NAMESPACE is null)
        // or the bracketed syntax (second child of AST_NAMESPACE is a statement) was used:
        // (1) if non-bracketed, the namespace must be set for all upcoming sister nodes until we encounter
        //     the next AST_NAMESPACE
        // (2) if bracketed, the namespace in principle only holds for the subtree rooted in the second child
        //     of AST_NAMESPACE (and should be set only for that subtree, but not for upcoming sister nodes);
        //     however, in this case the next sister node (if it exists) *must* be another
        //     AST_NAMESPACE node, according to PHP syntax (otherwise, a 'No code may exist outside of namespace {}'
        //     fatal error would be thrown at runtime.) Hence, if the next sister node is an AST_NAMESPACE anyway,
        //     the namespace will be set to something new once we finished off the subtree rooted in the
        //     second child of the AST_NAMESPACE we encountered.
        if( $child->kind === ast\AST_NAMESPACE) {
          $namespace = $child->children["name"] ?? "";
          $uses = []; // any namespace statement cancels all uses currently in effect
        }

        // If we encounter a child node that is a use node, add the translation rules specified by it
        // to the translation rules currently in effect
        if( $child->kind === ast\AST_USE) {
          $uses = array_merge( $uses, $this->getTranslationRulesForUse( $child));
        }

        // for the "stmts" child of an AST_CLASS, which is an AST_STMT_LIST,
        // we insert an artificial toplevel function node
        if( $ast->kind === ast\AST_CLASS && $childrel === "stmts") {
          $tnode = $this->store_toplevelnode( Exporter::TOPLEVEL_CLASS, $nodename, $nodeline, $nodeendline, $i, $funcid, $namespace);
          // when exporting the AST_STMT_LIST below the AST_CLASS, the
          // funcid is set to the toplevel node's id, childname is set to "stmts" (doesn't really matter, we can invent a name here), and childnum is set to 0
          $childnode = $this->export( $child, $tnode, $nodeline, "stmts", 0, $namespace, $uses, $classname);
          $this->store_rel( $tnode, $childnode, "PARENT_OF"); // AST_TOPLEVEL -> AST_STMT_LIST
          $this->store_rel( $rootnode, $tnode, "PARENT_OF"); // AST_CLASS -> AST_TOPLEVEL
        }
        // for the child of an AST_NAME node which is *not* fully qualified, we apply the translation rules currently in effect
        elseif( $ast->kind === ast\AST_NAME && $childrel === "name" && $ast->flags !== ast\flags\NAME_FQ) {
          $child = $this->applyTranslationRulesForName( $child, $uses);
          $childnode = $this->export( $child, $funcid, $nodeline, $childrel, $i, $namespace, $uses, $classname);
          $this->store_rel( $rootnode, $childnode, "PARENT_OF");
        }
        // in all other cases, we simply recurse straightforwardly
        else {
          $childnode = $this->export( $child, $funcid, $nodeline, $childrel, $i, $namespace, $uses, $classname);
          $this->store_rel( $rootnode, $childnode, "PARENT_OF");
        }

        // next child...
        $i++;
      }
    }

    // if $ast is not an AST node, it should be a plain value
    // see http://php.net/manual/en/language.types.intro.php

    // (2) if it is a plain value and more precisely a string, escape
    // it and put quotes around the content
    else if( is_string( $ast)) {

      $nodetype = gettype( $ast); // should be string
      $rootnode = $this->store_node( self::LABEL_AST, $nodetype, null, $nodeline, $this->quote_and_escape( $ast), $childnum, $funcid, $classname, $this->quote_and_escape( $namespace));
    }

    // (3) If it a plain value and more precisely null, there's no corresponding code per se, so we just print the type.
    // Note that this branch is NOT relevant for statements such as, e.g.,
    // $n = null;
    // Indeed, in this case, null would be parsed as an AST_CONST with appropriate children (see test-own/assignments.php)
    // Rather, we encounter a null node when things are undefined, such as, for instance, an array element's key,
    // a class that does not use an "extends" or "implements" statement, a function that has no return value, etc.
    else if( $ast === null) {

      $nodetype = gettype( $ast); // should be the string "NULL"
      $rootnode = $this->store_node( self::LABEL_AST, $nodetype, null, $nodeline, null, $childnum, $funcid, $classname, $this->quote_and_escape( $namespace));
    }

    // (4) if it is a plain value but not a string and not null, cast to string and store the result as $nodecode
    // Note: I expected at first that such values may be booleans, integers, floats/doubles, arrays, objects, or resources.
    // However, testing this on test-own/assignments.php, I found that this branch is only taken for integers and floats/doubles;
    // * for booleans (as for the null value), AST_CONST is used;
    // * for arrays, AST_ARRAY is used;
    // * for objects and resources, which can only be instantiated via the
    //   new operator or function calls, the corresponding statement is
    //   decomposed as an AST, i.e., we get AST_NEW or AST_CALL nodes with appropriate children.
    // Thus, so far I have only seen this branch taken for integers and floats/doubles.
    // We print these similarly as strings, but without quotes.
    else {

      $nodetype = gettype( $ast);
      $nodecode = (string) $ast;
      $rootnode = $this->store_node( self::LABEL_AST, $nodetype, null, $nodeline, $nodecode, $childnum, $funcid, $classname, $this->quote_and_escape( $namespace));
    }

    return $rootnode;
  }

  /*
   * Takes an AST_USE node and returns the array of translation rules it defines.
   */
  private function getTranslationRulesForUse( $astuse) : array {

    if( !($astuse instanceof ast\Node) || ($astuse->kind !== ast\AST_USE))
      throw new Exception("Illegal argument to getTranslationRulesForUse(): " . var_export($astuse, true));

    $uses = [];

    foreach( $astuse->children as $astuseelem) {
      $actual = $astuseelem->children["name"];
      // if no alias is given, the default one is the last part of the actual namespace
      $alias = $astuseelem->children["alias"] ?? substr( $actual, strrpos( $actual, "\\") + 1);
      $uses[$alias] = $actual;
    }

    return $uses;
  }

  /*
   * Takes a string and applies the given translation rules.
   * This function is applied in the context of an AST export where the given string
   * is a leaf node and a child of an AST_NAME node.
   */
  private function applyTranslationRulesForName( $haystack, $uses) : string {

    if( !is_string( $haystack))
      throw new Exception("Illegal argument to applyTranslationRulesForName(): " . var_export($haystack, true));

    foreach( $uses as $needle => $replacement) {
      $needle .= "\\";
      $replacement .= "\\";
      // crude imitation of startsWith( $haystack, $needle)
      if( substr( $haystack, 0, strlen( $needle)) === $needle)
        return $replacement . substr( $haystack, strlen( $needle));
    }

    return $haystack;
  }

  /*
   * (Abstract) helper function to write a node to a file and increase
   * the node counter.
   *
   * Note on node types: there are different types of nodes:
   * - AST_* nodes with children of their own; these can be divided in two kinds:
   *   i. normal AST nodes
   *   ii. declaration nodes (see https://github.com/nikic/php-ast/issues/12)
   * - strings, for names of variables and constants, for the content
   *   of variables, etc.
   * - NULL nodes, for undefined nodes in the AST
   * - integers and floats/doubles, i.e., plain types
   * - File and Directory nodes, for files and directories,
   *   representing the global code structure (we use store_filenode()
   *   and store_dirnode() for these)
   *
   * The following properties are inherited from PHP ASTs for all nodes (see https://github.com/nikic/php-ast)
   * @param label    The node label (mandatory)
   * @param type     The node type (mandatory)
   * @param flags    The node's flags (mandatory, but may be empty)
   * @param lineno   The node's line number (mandatory)
   * Note that an ast\Node's fourth property, namely, children, are not passed to this function, obviously.
   * They will be stored on their own and the relationships will be stored by the function store_rel()
   *
   * The following properties are meta-properties that we use for internal purposes as well as for
   * importing ASTs into Joern:
   * @param code      The node code, set only for nodes that are not instances of ast\Node. In these
   *                  cases, the "node" is simply cast to a string passed as $code to this function.
   *                  Such nodes are primitive types: strings, integers, doubles... (optional)
   * @param childnum  The child number of this node, i.e., how many older siblings it has ;-) (optional)
   * @param funcid    The id of the function node that this node is a part of (optional)
   * @param classname The name of the class node that this node is a part of (optional)
   * @param namespace The namespace that this node belongs to (optional)
   *
   * Additionally, only for decl nodes, i.e., function and class declarations (thus obviously optional), the
   * following properties are again inherited from the PHP ASTs (see https://github.com/nikic/php-ast)
   * @param endlineno  The node's last line number
   * @param name       The function's or class's name
   * @param doccomment The function's or class's doc comment
   *
   * @return The index of the stored node.
   */
  abstract protected function store_node( $label, $type, $flags, $lineno, $code = null, $childnum = null, $funcid = null, $classname = null, $namespace = null, $endlineno = null, $name = null, $doccomment = null) : int;

  /*
   * (Abstract) helper function to writes a relationship to a file.
   *
   * @param start   The starting node's index
   * @param end     The ending node's index
   * @param type    The relationship's type
   */
  abstract public function store_rel( $start, $end, $type);

  /**
   * Stores a file node, increases the node counter and returns the
   * index of the stored file node.
   *
   * @param $filename The file's name, which will be stored under the
   *                  'name' poperty of the File node.
   *
   * @return The index of the stored file node.
   */
  public function store_filenode( $filename) : int {

    return $this->store_node( self::LABEL_FS, self::FILE, null, null, null, null, null, null, null, null, $this->quote_and_escape( $filename), null);
  }

  /**
   * Stores a "fake" AST toplevel function node, increases the node
   * counter and returns the index of the stored toplevel node. We use
   * toplevel nodes to encapsulate toplevel functions defined by File
   * or class nodes:
   *
   * File --[FILE_OF]--> AST_TOPLEVEL --[PARENT_OF]--> AST_STMT_LIST
   * AST_CLASS --[PARENT_OF]--> (extends)
   *           --[PARENT_OF]--> (implements)
   *           --[PARENT_OF]--> AST_TOPLEVEL --[PARENT_OF]--> AST_STMT_LIST
   *
   * @param $name      The name of the toplevel node. We use the path for
   *                   AST_TOPLEVEL nodes under File nodes, and the class
   *                   name for AST_TOPLEVEL nodes under class nodes (mandatory)
   * @param $flag      The kind of toplevel node: TOPLEVEL_FILE or TOPLEVEL_CLASS (mandatory)
   * @param $lineno    The starting line number of the toplevel node. Should equal starting
   *                   line number of class node for toplevel nodes under class nodes and
   *                   1 for toplevel nodes under file nodes (mandatory)
   * @param $endlineno The end line number of the toplevel node. Should equal end line number
   *                   of class node for toplevel nodes under class nodes and the number of
   *                   lines in a file for toplevel nodes under file nodes (mandatory)
   * @param $childnum  The childnum of the toplevel node: This is only relevant for
   *                   toplevel nodes under classes, and should always equal 2 in
   *                   this case (see above: 0=extends; 1=implements; 2=AST_TOPLEVEL)
   * @param $funcid    The funcid of the toplevel node: Again, only relevant for
   *                   toplevel nodes under classes, where the funcid should equal
   *                   the toplevel node's id of the file.
   * @param $namespace The namespace of the toplevel node: Again, only relevant for
   *                   toplevel nodes under classes, where the namespace should equal
   *                   the namespace of the class.
   *
   * @return The index of the stored toplevel node.
   */
  public function store_toplevelnode( $flag, $name, $lineno, $endlineno, $childnum = null, $funcid = null, $namespace = null) : int {

    $tnode = $this->store_node( self::LABEL_AST, self::TOPLEVEL, $flag, $lineno, null, $childnum, $funcid, null, $this->quote_and_escape( $namespace), $endlineno, $this->quote_and_escape( $name), null);

    // For toplevel nodes, we create artificial entry and exit nodes (like file and dir nodes,
    // they are not actually part of the AST).
    // For the entry and exit nodes, we only set
    // (1) the funcid (to the id of the toplevel node), and
    // (2) the name (to that of the file or class)
    $entrynode = $this->store_node( self::LABEL_ART, self::FUNC_ENTRY, null, null, null, null, $tnode, null, null, null, $this->quote_and_escape( $name), null);
    $exitnode = $this->store_node( self::LABEL_ART, self::FUNC_EXIT, null, null, null, null, $tnode, null, null, null, $this->quote_and_escape( $name), null);
    $this->store_rel( $tnode, $entrynode, "ENTRY");
    $this->store_rel( $tnode, $exitnode, "EXIT");

    return $tnode;
  }

  /**
   * Stores a directory node, increases the node counter and returns the
   * index of the stored directory node.
   *
   * @param $dirname The directory's name, which will be stored under the
   *                 'name' poperty of the Directory node.
   *
   * @return The index of the stored directory node.
   */
  public function store_dirnode( $filename) : int {

    return $this->store_node( self::LABEL_FS, self::DIR, null, null, null, null, null, null, null, null, $this->quote_and_escape( $filename), null);
  }

  /**
   * (Abstract) helper function to escape strings that are to be
   * stored as node properties in such a way that they will not
   * conflict with the concrete syntax of a particular file format
   * targeted by implementing classes when exporting nodes.
   *
   * @param $str  The string to be quoted and escaped
   *
   * @return $str The quoted and escaped string
   */
  abstract protected function quote_and_escape( $str) : string;

  /*
   * Slight modification of format_flags() from php-ast's util.php
   *
   * Given a kind (e.g., AST_NAME or AST_METHOD) and a set of flags
   * (say, NAME_NOT_FQ or MODIFIER_PUBLIC | MODIFIER_STATIC), both of
   * which are represented as an integer, return the named list of
   * flags as a list that is represented as a string and whose
   * elements are separated by $this->array_delim.
   *
   * Some flags are exclusive (say, NAME_FQ and NAME_NOT_FQ, for the
   * AST_NAME kind), while others are combinable (say, MODIFIER_PUBLIC
   * and MODIFIER_STATIC, for the AST_METHOD kind). Each kind has at
   * most one exclusive flag, but may have more than one combinable
   * flag. Additionally, no kind uses both exclusive and combinable
   * flags, i.e., the set of kinds using exclusive flags and the set of
   * kinds using cominable flags are disjunct.
   *
   * More information on flags can be found by looking at the source
   * code of the function get_flag_info() in util.php
   *
   * @param kind  An AST node type, represented as an integer
   * @param flags Flags pertaining to the current AST node, represented
   *              as an integer
   *
   * @return A list of named flags, represented as a string.
   */
  protected function format_flags( int $kind, int $flags) : string {

    list( $exclusive, $combinable) = get_flag_info();
  
    // ast\AST_ARRAY_ELEM and ast\AST_CLOSURE_VAR nodes use an exclusive
    // flag (the integer 1) which does not have an appropriate constant declared
    // in ast\flags. This flag is used when an array element or a variable used
    // by a closure is referenced "by reference", e.g., in code such as
    //   [&$a];
    //   function() use(&$b) {};
    // See https://github.com/nikic/php-ast#flags
    // Until such a constant is registered in the php-ast extension, we add
    // a custom flag name "BY_REFERENCE" for the two nodes that use it.
    $exclusive[ast\AST_ARRAY_ELEM] = [1 => "BY_REFERENCE"];
    $exclusive[ast\AST_CLOSURE_VAR] = [1 => "BY_REFERENCE"];

    if( isset( $exclusive[$kind])) {
      $flagInfo = $exclusive[$kind];
      if( isset( $flagInfo[$flags])) {
        return $flagInfo[$flags];
      }
    }

    else if( isset( $combinable[$kind])) {
      $flagInfo = $combinable[$kind];
      $names = [];
      foreach( $flagInfo as $flag => $name) {
        if( $flags & $flag) {
          $names[] = $name;
        }
      }
      if( !empty($names)) {
        return implode( $this->array_delim, $names);
      }
    }

    // If the given $kind does not use either exclusive or combinable
    // flags, or if it does, but the given $flags did not yield any
    // flags for the given $kind, we arrive here. In principle $flags
    // should always be 0 at this point.
    // TODO: for ast\AST_ARRAY_ELEM (kind=525) and ast\AST_CLOSURE_VAR
    // (kind=2049), the flag might be 1, meaning "by-reference", but
    // this cannot be properly formated since no appropriate names are
    // declared in util.php. Ask Niki about that. Maybe submit patch.
    if( $flags === 0)
      return "";
    else
      return "\"[WARNING] Unexpected flags for kind: kind=$kind and flags=$flags\"";
  }

  /**
   * Returns the number of nodes created so far.
   *
   * @return The number of nodes created so far.
   */
  public function getNodeCount() : int {
    return $this->nodecount;
  }
}


/**
 * Custom error class for IO errors
 */
class IOError extends Error {}
