
FROM redislabs/redistimeseries:latest as redistimeseries
FROM redislabs/rejson:latest as rejson
FROM redislabs/rebloom:latest as rebloom

FROM redislabs/redisgears:edge as redis
ENV LIBDIR /usr/lib/redis/modules
WORKDIR /data
RUN set -ex;\
    apt-get update;\
    mkdir -p ${LIBDIR};
COPY --from=rebloom ${LIBDIR}/rebloom.so ${LIBDIR}
COPY --from=redistimeseries ${LIBDIR}/redistimeseries.so ${LIBDIR}
COPY --from=rejson ${LIBDIR}/rejson.so ${LIBDIR}
CMD ["--loadmodule", "/usr/lib/redis/modules/rejson.so", \
    "--loadmodule", "/usr/lib/redis/modules/redistimeseries.so", \
    "--loadmodule", "/usr/lib/redis/modules/rebloom.so",\
    "--loadmodule", "/usr/lib/redis/modules/redisgears.so",\
    "PythonHomeDir", "/usr/lib/redis/modules/deps/cpython/"]