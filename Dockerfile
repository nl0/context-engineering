FROM alpine:3.21

RUN apk add --no-cache pandoc-cli tectonic font-roboto font-roboto-mono fontconfig \
    && fc-cache -f

WORKDIR /course
ENTRYPOINT ["pandoc"]
