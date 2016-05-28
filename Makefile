
all:
	echo "You need a target, please"

coffee:
	python ./src/coffee-proto-client.py $(IP) $(PORT)
