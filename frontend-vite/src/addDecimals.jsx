function addDecimals(a, b) {
    const validate = str => str.includes(".") ? str : str + ".00"
    const getCents = str => parseInt(str.slice(0, str.length - 3) + str.slice(str.length - 2))

    a = validate(a)
    b = validate(b)

    let sum = getCents(a) + getCents(b)
    let sumStr = sum.toString()
    let periodIndex = sumStr.length - 2
    let result = sumStr.slice(0, periodIndex) + "." + sumStr.slice(periodIndex)

    return result
}

export default addDecimals