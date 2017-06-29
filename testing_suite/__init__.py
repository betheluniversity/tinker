"""

'Integration testing exercises two or more parts of an application at once, including the interactions between the
parts, to determine if they function as intended. This type of testing identifies defects in the interfaces between
disparate parts of a codebase as they invoke each other and pass data between themselves.

While unit testing is used to find bugs in individual functions, integration testing tests the system as a whole.'



Based off of the paradigm described above, the integration_tests folder has tests in it that test connecting to an
endpoint on the tinker webpage and making sure that it returns the correct HTML based off of the parameters passed to
it from the URL args and any POST data it may have. On the other hand, the unit_tests folder will test the individual
functions themselves, making sure that passing in specific sets of arguments will return the correct response and other
sets will break the function intentionally.

"""
