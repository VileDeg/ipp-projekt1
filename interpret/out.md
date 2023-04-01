<!DOCTYPE html>
<head>
    <meta charset="UTF-8">
    <meta name="description" content="Test results">
    <style>
    th, td { padding-left:10px; padding-right:10px; color:white; }
    h1,h2,h3,h4 { color:white; }
    textarea { background-color: rgb(18, 18, 18); color:white; }
    body { padding-left: 1em; padding-right: 1em; background-color: rgb(18, 18, 18); }
    </style>
</head>

<body>
    <h1 style="text-align: center;">Test result</h1>
    <h2>Tests run: 18</h2>
    <h2>Passed: 4 </h2>
    <h2>Failed: 14 </h2>
    <hr>
    <h3 style="text-align: center; color:red">Failed tests</h3><hr><h4>../ipp-2023-tests/interpret-only/curr/arithmetic</h4><table><tr><th>Test name</th><th>Return code</th><th>Expected return code</th><th>Output</th><th>Expected output</th></tr>
<tr><td>incorrectInt</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50></textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>zeroDiv</td><td>0</td><td>57</td><td><textarea readonly rows=5 cols=50></textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

</table>
<hr><h4>../ipp-2023-tests/interpret-only/curr/32</h4><table><tr><th>Test name</th><th>Return code</th><th>Expected return code</th><th>Output</th><th>Expected output</th></tr>
<tr><td>bad_argument_tag</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50></textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>bad_root_element</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50></textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>duplicit_order</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50>0abc</textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>missing_argument</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50>0</textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>missing_opcode</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50></textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>missing_order</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50></textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>negative_order</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50>abc0</textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>string_order</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50></textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>unknown_element</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50></textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>unknown_element2</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50></textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>write_test</td><td>0</td><td>32</td><td><textarea readonly rows=5 cols=50>0</textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

</table>
<hr><h4>../ipp-2023-tests/interpret-only/curr/31</h4><table><tr><th>Test name</th><th>Return code</th><th>Expected return code</th><th>Output</th><th>Expected output</th></tr>
<tr><td>fucked_up_xml</td><td>0</td><td>31</td><td><textarea readonly rows=5 cols=50></textarea></td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

</table>
<hr><h3 style="text-align: center; color:green">Passed tests</h3><hr><h4>../ipp-2023-tests/interpret-only/curr/arithmetic</h4><table><tr><th>Test name</th><th>Return code</th><th>Output</th></tr>
<tr><td>correct</td><td>0</td><td><textarea readonly rows=5 cols=50>3</textarea></td></tr>

<tr><td>negativeNum</td><td>0</td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>nil</td><td>53</td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

<tr><td>stringAdd</td><td>53</td><td><textarea readonly rows=5 cols=50></textarea></td></tr>

</table>
</body></html>