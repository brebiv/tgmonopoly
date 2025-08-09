# ssh -v -N -R 9000:localhost:8000 leonid@vystava-01
ssh -v -R 9000:localhost:8000 leonid@vystava-01 "while true; do date; sleep 1; done"
