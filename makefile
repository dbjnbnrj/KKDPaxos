
PID = 0

basic:
	python balanceSystem.py ${PID}

imp:
	python balanceSystem.py ${PID} -imp

clean:
	-rm balance_log

