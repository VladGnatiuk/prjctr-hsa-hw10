FROM httpd:2.4

WORKDIR /tests
COPY load_test.sh .
RUN chmod +x load_test.sh

ENTRYPOINT ["./load_test.sh"]