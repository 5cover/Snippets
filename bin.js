/**
 *
 * @param {number} min
 * @param {number} max
 */
function bin(min, max) {
    const imin = Math.ceil(min), imax = Math.floor(max);
    if (min !== imin) {
        console.log(`${imin - 1} : ${imin - min}`);
    }
    for (let i = imin; i < imax; ++i) {
        console.log(`${i} : 1`);
    }
    if (max !== imax) {
        console.log(`${imax} : ${max - imax}`);
    }
}
