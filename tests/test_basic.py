from gwPackage import helo
from gwPackage.core import ad
from gwPackage.core import add
def test_hello():
	assert hello() == "gwPackage is working"

def test_add():
	assert add(2, 3) == 5
