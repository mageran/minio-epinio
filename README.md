# Enabling Minio in Epinio

Epinio comes with a running [Minio](https://min.io/) installation, which is used internally to store source code. The following can be used to (1) expose this service externally and (2) to use it within epinio apps through a service (similiar to redis, mysql etc).

## Exposing the Minio service externally

The minio service can be exposed externally by running

```
make expose-minio
```

By default, it uses `minio.127.0.0.1.sslip.io` as host name where minio is accessible. In order to use a different name, the env variable MINIO_HOST can be set:

```
MINIO_HOST=myhost.example.com make expose-minio
```

### Testing the service using aws cli

The Makefile has rules to setup and test the service using the aws command line interface (installation instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)). The command

```
make aws-setup
```

performs the configuration setup, and 

```
make aws-test
```

runs an "ls" command that should respond with the list of buckets.

## Enabling the use of minio in epinio apps

The minio service can be registered in the epinio service catalog using the command:

```
make register-minio-catalog-service
```

It will create the required kubernetes resources to enable epinio app developers to use epinio following the same mechanism as the other built-in services like mysql, redis, etc. The minio service will show up as `minio-service-dev` in the catalog list:

```
> epinio service catalog

🚢  Getting catalog...

✔️  Epinio Services:
|       NAME        |            CREATED            | VERSION |          DESCRIPTION           |
|-------------------|-------------------------------|---------|--------------------------------|
| rabbitmq-dev      | 2023-02-20 20:16:35 -0800 PST | 3.11.5  | A RabbitMQ service that can be |
|                   |                               |         | used during development        |
| redis-dev         | 2023-02-20 20:16:35 -0800 PST | 7.0.7   | A Redis service that can be    |
|                   |                               |         | used during development        |
| mysql-dev         | 2023-02-20 20:16:35 -0800 PST | 8.0.31  | A fabulous MYSQL service       |
|                   |                               |         | that can never be used during  |
|                   |                               |         | development                    |
| postgresql-dev    | 2023-02-20 20:16:35 -0800 PST | 15.1.0  | A PostgreSQL service that can  |
|                   |                               |         | be used during development     |
| mongodb-dev       | 2023-02-20 20:16:35 -0800 PST | 6.0.3   | A MongoDB service that can be  |
|                   |                               |         | used during development        |
| minio-service-dev | 2023-04-06 11:13:53 -0700 PDT | v1      | A Minio service that can be    |
|                   |                               |         | used during development        |
```

In the following we use `devMinio` as service name and `pyhw` as app name.

The service (instance) is created with

```
epinio service create minio-service-dev devMinio
```

We can verify the creation using `epinio service list` and `epinio service show devMinio`

The output for the latter should look something like that:
```
|       KEY       |             VALUE             |
|-----------------|-------------------------------|
| Name            | devMinio                      |
| Created         | 2023-04-06 14:42:46 -0700 PDT |
| Catalog Service | minio-service-dev             |
| Version         | v1                            |
| Status          | deployed                      |
| Used-By         |                               |
| Internal Routes |                               |
```


The service can then be bound to the app using 

```
epinio service bind devMinio pyhw
```

As a result, we should now see a configuration being created:

```
epinio configuration list


🚢  Listing configurations
Namespace: ....

✔️  Epinio Configurations:
|                      NAME                       |            CREATED            |  TYPE   |    ORIGIN     |          APPLICATIONS          |
|-------------------------------------------------|-------------------------------|---------|---------------|--------------------------------|
| x3b302cdc9c34cf4411bce2b95f13-minio-service-dev | 2023-04-06 14:42:48 -0700 PDT | service | devMinio      | pyhw (migrate to new access    |
|                                                 |                               |         |               | paths)                         |

```

This configuration defines the following parameter, which can be used inside the app to access the minio service (for instance with the [Boto3 client](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) in python).

```
epinio configuration show x3b302cdc9c34cf4411bce2b95f13-minio-service-dev
...
|   PARAMETER    |                      VALUE                       |               ACCESS PATH               |
|----------------|--------------------------------------------------|-----------------------------------------|
| accesskey      | XXXXXXXXXXXXXXXX                                 | /configurations/devMinio/accesskey      |
| endpoint_url   | https://minio-x3b302cdc9c34cf4411bce2b95f13:9000 | /configurations/devMinio/endpoint_url   |
| s3_bucket_name | x3b302cdc9c34cf4411bce2b95f13.phase1.s3.bucket   | /configurations/devMinio/s3_bucket_name |
| secretkey      | XXXXXXXXXXXXXXXX                                 | /configurations/devMinio/secretkey      |
```

As you can see, a bucket has been created that can be used by the application. The instance name and namespace have been used to name the bucket to avoid name clashes with other apps.


## References:

* Github repository for the code implemeting the helm-chart of the minio service: [here](https://github.com/mageran/kubernetes-epinio).

* Github repository and pages for helm-chart repo where the helm chart of the service is uploaded to: [here](https://github.com/mageran/helm-charts-repo)