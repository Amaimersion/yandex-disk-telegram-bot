'use strict';


async function main() {
    await run_redirect();
}


async function run_redirect() {
    const element = document.getElementById('redirect-message');
    let redirectUrl = element.dataset.redirectUrl.trim();

    if (!redirectUrl) {
        return;
    }

    let redirectSeconds = 5;

    while (redirectSeconds >= 0) {
        element.innerText = (
            'You will be automatically redirected to the bot ' +
            `in ${redirectSeconds}.`
        );

        if (redirectSeconds > 0) {
            await new Promise((resolve) => {
                window.setTimeout(
                    () => resolve(),
                    1000
                );
            });
        }

        redirectSeconds--;
    }

    const fallbackElement = document.createElement('span');
    const linkElement = document.createElement('a');

    fallbackElement.innerHTML = '&nbsp;';
    linkElement.innerText = "Click here if it didn't happen.";
    linkElement.href = redirectUrl;

    fallbackElement.appendChild(linkElement);
    element.appendChild(fallbackElement);

    window.location.href = redirectUrl;
}


if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
} else {
    main();
}
