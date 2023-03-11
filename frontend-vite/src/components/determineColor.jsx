function determineColor(status) {
    let color

    switch(status) {
        case "Created":
            color = "#FFF3BF"
            break
        case "Sent":
            color = "#D0EBFF"
            break
        case "Received":
            color = "#D3F9D8"
            break
        case "Canceled":
            color = "#DBE4FF"
            break
        default:
            color = "#F1F3F5"
            break
    }

    return color
}

export default determineColor