pars_dir=parser
interp_dir=interpret

pars_in=$pars_dir/in.ifjc23
interp_in=$interp_dir/src.xml

# Run the parser
php8.1 $pars_dir/parse.php < $pars_in > $interp_in
python3 $interp_dir/interpret.py --source=$interp_in
# Print return code
echo $?