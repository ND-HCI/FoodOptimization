// TODO: maybe use a better function that covers all cases
function escapeHTML(string) {
    string = string.replaceAll('&amp;', '&');
    string = string.replaceAll('&lt;', '<');
    string = string.replaceAll('&gt;', '>');
    string = string.replaceAll('&#39;', "'");
    string = string.replaceAll('&#34;', '"');
    string = string.replaceAll('&quot;', '"');
    return string;  // return translated/updated string
} 

function toTitleCase(st) {
    st = st.toLowerCase().split(" ").reduce( (s, c) => s + "" + (c.charAt(0).toUpperCase() + c.slice(1) +" "), '');
    return st
}