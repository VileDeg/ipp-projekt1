testPath=tests/parser
test=write_test
testOut=${test}.out
myOut=out.xml
myIn=in.ifjc22

php8.1 parse.php < $testPath/$1.src
#diff $testPath/${test}.out out.xml