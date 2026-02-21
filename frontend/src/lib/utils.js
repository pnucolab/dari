export function formatDate(datestr) {
    const date = new Date(datestr);

    const pad = (num) => String(num).padStart(2, '0');

    const formattedDate = 
        `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ` +
        `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;

    return formattedDate;
}