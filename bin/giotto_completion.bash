_giotto() 
{
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    if [[ ${prev} == cmd ]] ; then
        COMPREPLY=( $(giotto suggest ${cur}) )
        return 0
    fi
}
complete -o nospace -F _giotto giotto