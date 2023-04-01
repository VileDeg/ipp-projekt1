<?php

define('HEADER', 'IPPcode23'); //Header of IPPcode23 source file

class Singleton { //Singleton pattern. Inspired by https://refactoring.guru/design-patterns/singleton/php/example
    private static $instances = [];

    protected function __construct() { } //Prevent direct creation of object

    protected function __clone() { } //Prevent cloning of object

    public static function getInstance() 
    {
        $subClass = static::class;
        if (!isset(self::$instances[$subClass])) {
            self::$instances[$subClass] = new static();
        }
        return self::$instances[$subClass];
    }
}

class Token {
    public $str; //String representation of token
    public $args; //Array of argument types
    public $isopcode; //Is token an opcode?
    public $type; //Type of token
    public $value; //Value of token
    public $linenum; //Number of line in source file where token was found

    function __construct($word) {
        $this->str = $word;
        $this->args = [];
        $this->isopcode = false;
        $this->type = '';
        $this->value = '';

        $this->testOpcode();
    }

    private function testOpcode() {
        switch (strtoupper($this->str)) {
            case 'CREATEFRAME': case 'PUSHFRAME': case 'POPFRAME': case 'RETURN': case 'BREAK':
                break;
            case 'DEFVAR': case 'POPS':
                $this->args = ['var'];
                break;
            case 'PUSHS': case 'WRITE': case 'EXIT': case 'DPRINT':
                $this->args = ['symb'];
                break;
            case 'CALL': case 'LABEL': case 'JUMP':
                $this->args = ['label'];
                break;
            case 'INT2CHAR': case 'STRLEN': case 'TYPE': case 'MOVE': case 'NOT':
                $this->args = ['var', 'symb'];
                break;
            case 'READ':
                $this->args = ['var', 'type'];
                break;
            case 'ADD': case 'SUB': case 'MUL': case 'IDIV': case 'LT': case 'GT': case 'EQ': 
            case 'AND': case 'OR': case 'STR2INT': case 'CONCAT': case 'GETCHAR': case 'SETCHAR': 
            case 'STRI2INT':
                $this->args = ['var', 'symb', 'symb'];
                break;
            case 'JUMPIFEQ': case 'JUMPIFNEQ':
                $this->args = ['label', 'symb', 'symb'];
                break;
            default:
                $this->isopcode = false;
                return;
        }
        
        $this->isopcode = true;
    }

    function testArgument($argi, &$argtk) {
        static $specreg = '_\-$&%*!?';
        $idreg = '['.$specreg.'a-z]['.$specreg.'\w]*';
        $varreg = '/^[GLT]F@'.$idreg.'$/u';
        
        $argtype = $this->args[$argi];
        //$argstr = $argtk->str;
        $argtk->type = $argtype;
        $argtk->value = $argtk->str;

        if ($argtype != 'label' && $argtk->isopcode) {
            return false; //invalid argument error
        }

        switch ($argtype) {
            case 'var':
                return preg_match($varreg, $argtk->str);
            case 'type':
                return preg_match('/^(int|bool|string|nil)$/u', $argtk->str);
            case 'label':
                return preg_match('/^'.$idreg.'$/iu', $argtk->str);
            case 'symb':
                if (preg_match('/^int@[+-]?\d+$/u', $argtk->str)) {
                    $argtk->type = 'int';
                    $argtk->value = substr($argtk->str, 4);
                } else if (preg_match('/^bool@(true|false)$/u', $argtk->str)) {
                    $argtk->type = 'bool';
                    $argtk->value = substr($argtk->str, 5);
                } else if (preg_match('/^string@([^\\\\\s#]|\\\\\d{3})*$/u', $argtk->str)) {
                    $argtk->type = 'string';
                    $argtk->value = substr($argtk->str, 7);
                } else if (preg_match('/^nil@nil$/u', $argtk->str)) {
                    $argtk->type = 'nil';
                    $argtk->value = substr($argtk->str, 4);
                } else if (preg_match($varreg, $argtk->str)) { //Variable
                    $argtk->type = 'var';
                } else {
                    return false;
                }
                return true;
            default:
                return false;
        }
    }

    function isHeader() {
        return $this->str == '.'.HEADER;
    }
}

class Parser extends Singleton { 
    public $tokens; //Array of tokens

    protected function __construct() {
        $this->tokens = [];
    }
    
    private function pushToken($word, $linenum) { //Push token to array and check for multiple opcodes in one line
        $newtk = new Token($word);
        $newtk->linenum = $linenum;
        $this->tokens[] = $newtk;

        if ($newtk->isopcode && !$this->singleOpcodeOnOneLine($linenum)) {
            exitprint("Multiple opcodes in one line.", 23);
        }
    }

    private function singleOpcodeOnOneLine($linenum) { //Check if there is only one opcode in current line
        for ($i = count($this->tokens)-2; $i >= 0; --$i) { //Iterate through tokens in reverse order
            $tk = $this->tokens[$i];
            if ($tk->linenum != $linenum) { //If token is not in current line
                break;
            }

            if ($tk->isopcode) { //Opcode vs label edge case
                for ($j = 0; $j < count($tk->args); ++$j) { //Iterate through previous opcode arguments
                    if ($tk->args[$j] == 'label') { //If argument is label, new token is not opcode but label
                        return true;
                    }
                }
                return false;
            }
        }
        return true;
    }

    function getTokens($fileHandle) { //Get tokens from file

        for ($i = 0; $line = fgets($fileHandle); ++$i){
            $lnwrds = mb_split('\s+', $line); //Split line into words

            foreach ($lnwrds as $wrd) { //Iterate through words
                $wrd = trim($wrd);
                
                if (str_contains($wrd, '#')) { 
                    if ($wrd[0] != '#') { //If there's no whitespace between token and comment.
                        $this->pushToken(substr($wrd, 0, strpos($wrd, '#')), $i);
                    }
                    break; //Comment found, skip rest of line
                } else if (!empty($wrd)) { 
                    $this->pushToken($wrd, $i);
                }
            }
        }

        if (!$this->tokens[0]->isHeader()) { //Check if header is present
            exitprint("Missing header in source file.", 21);
        }
        
        array_splice($this->tokens, 0, 1); //Remove header from array of tokens
    }
}

function exitprint($str, $code) { //Print error message and exit with error code
    fwrite(STDERR, "[Error ".$code."]: ".$str."\n");
    exit($code);
}

function parseCmdArguments() { //Parse command line arguments
    static $helpText = "Name:\n\t".
        "parse.php - IPPcode23 code parser.\n\n".
        "Usage:\n\tparse.php [--help]\n\nDescription:\n\t".
        "Parses IPPcode23 source code. Checks for lexical and syntax errors. Input from STDIN.\n\n".
        "Options:\n\t--help\n\t\tPrints the help message.\n";

    $longopts  = array("help");
    $options = getopt(NULL, $longopts);

    if (!empty($options)) {
        if (count($options) == 1 && array_key_exists('help', $options)) {
            echo $helpText;
            exit(0);
        } else {
            exitprint("Invalid command line arguments.", 10);
        }
    }
}

ini_set('display_errors', 'stderr');
if (!mb_regex_encoding("UTF-8")) {
    exitprint("Encoding unavailable.", 99);
}

parseCmdArguments(); //Parse command line arguments

$parser = Parser::getInstance(); //Can't directly call constructor because of Singleton
$parser->getTokens(STDIN); 

$xw = new XMLWriter();

if (!$xw->openMemory()) {
    exitprint("Failed to allocate memory.", 99);
}
$xw->setIndent(1);
$xw->setIndentString(' ');
$xw->startDocument("1.0", "UTF-8"); //<

$xw->startElement('program'); //<+

$xw->startAttribute('language'); //<+*
    $xw->text(HEADER);
$xw->endAttribute(); //+*>

$insti = 1; //Instruction counter
for ($i = 0; $i < count($parser->tokens); ++$i, ++$insti) {
    $optk = $parser->tokens[$i];

    $xw->startElement('instruction'); //<++

    $xw->startAttribute('order'); //<++*
        $xw->text(strval($insti));
    $xw->endAttribute(); //++*>

    if (!$optk->isopcode) {
        exitprint("Invalid or unknown opcode.", 22);
    }

    $xw->startAttribute('opcode'); //<++*
        $xw->text(strtoupper($optk->str));
    $xw->endAttribute(); //++*>

    for ($j = 0; $j < count($optk->args); ++$j) {
        if (++$i >= count($parser->tokens)) {
            exitprint("Missing argument.", 23);
        }
        $argtk = $parser->tokens[$i];

        if (!$optk->testArgument($j, $argtk)) { //Check if argument is valid
            exitprint("Invalid argument.", 23);
        }

        $xw->startElement('arg'.strval($j+1)); //<+++
            
            $xw->startAttribute('type'); //+++*>
                $xw->text($argtk->type);
            $xw->endAttribute(); //<+++*

            $xw->text($argtk->value);

        $xw->endElement(); //+++>
    }

    if ($i+1 < count($parser->tokens)) {
        $optk = $parser->tokens[$i+1];
        if (!$optk->isopcode) { 
            exitprint("Too many arguments.", 23);
        }
    }

    $xw->endElement(); //++>
}

$xw->endElement(); //+>


$xw->endDocument(); //>
echo $xw->outputMemory(); //Print XML

exit(0);
?>