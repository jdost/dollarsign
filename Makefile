PYTHONPATH = PYTHONPATH=$(PWD)/src

.DEFAULT: shell

.PHONY: shell clean

shell:
	@${PYTHONPATH} python ./etc/console.py

clean:
	@rm -f src/*.pyc
	@rm -rf src/__pycache__
	@rm -f src/*/*.pyc
	@rm -rf src/*/__pycache__
