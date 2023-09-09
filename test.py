import pytest
 import functions
 import time

 def test_readStateFile(tmp_path):
     # Create a temporary file with test data
     test_file = tmp_path / "test.txt"
     test_file.write_text("amount,data,price")

     # Call the function with the test file
     arrdata = functions.readStateFile(test_file)
     result  = arrdata[0].price
     # Assert that the result is equal to the expected output
     assert result == "price"
