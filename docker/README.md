## About

This folder contains `Dockerfile` or configuration files for Docker images that are related to the application.

### Description

- `app` - main application image, which can be runned in standalone. It is production build.
- `rq` - RQ workers which can perform background tasks. If you use RQ in the app, then you should run this image along with the app image. It is production build.
- `nginx` - contains configuration volume for `nginx` image. This configuration implements the application expectations.

### Build

Run these commands to build these images:

- to build the `app`:

```shell
docker build --tag <NAME> -f ./docker/app/Dockerfile .
```

- to build the `rq`:

```shell
docker build --tag <NAME> -f ./docker/rq/Dockerfile .
```

Keep in mind that `rq` still depends on `amaimersion/yd-tg-bot-app`. You will need to change `Dockerfile` of `app` image in order to use your own image.
