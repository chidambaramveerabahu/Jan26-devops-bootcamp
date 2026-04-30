# build layer packace

docker run --platform linux/amd64 -v \
"$PWD":/var/task "public.ecr.aws/sam/build-python3.14" /bin/sh \
-c "pip install -r requirements.txt -t python/; exit"


# zip the layer package

zip -r psy-bin.zip python/

upload to create layers