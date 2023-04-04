pars_dir=./parser
interp_dir=./interpret
interp_src="$interp_dir/interpret.py $interp_dir/base.py $interp_dir/classes.py $interp_dir/error.py $interp_dir/globals.py $interp_dir/instructions.py"

zip -j xgonce00.zip $pars_dir/parse.php $pars_dir/readme1.md \
$interp_src $interp_dir/readme2.md \
rozsireni 
