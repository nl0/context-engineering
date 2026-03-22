FROM alpine:3.21

RUN apk add --no-cache pandoc-cli tectonic

WORKDIR /course
ENTRYPOINT ["pandoc"]
