FROM quay.io/keycloak/keycloak:latest

ENV KC_DB=postgres

RUN /opt/keycloak/bin/kc.sh build