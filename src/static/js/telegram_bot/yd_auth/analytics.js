function main() {
    const main = document.getElementsByTagName("main")[0];
    const status = main.dataset.status;

    gtag(
        "event",
        "yandex_disk_authorization",
        {
            "event_category": "authorization",
            "event_label": status
        }
    );
}


if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
} else {
    main();
}
