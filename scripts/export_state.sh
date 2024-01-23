while IFS='=' read -r key value; do
    if [[ -n $key && -n $value ]]; then
        # Check if the value is in the secret format
        if [[ $value == \$\(*\) || $value == \${{ secrets.* }} ]]; then
            is_secret=true
        else
            is_secret=false
        fi

        # Print the variable (for debugging purposes, you might want to remove this in production)
        echo "$key=$value"

        case $PLATFORM in
        'github')
            # Handling for GitHub Actions
            if [ "$is_secret" = true ]; then
                # Treat as a secret
                echo "$key=$value" >> $GITHUB_ENV
            else
                echo "$key='$value'" >> $GITHUB_ENV
            fi
            ;;
        'azdo')
            # Handling for Azure DevOps
            if [ "$is_secret" = true ]; then
                # Treat as a secret
                echo "##vso[task.setvariable variable=$key;isSecret=true]$value"
            else
                export "$key=$value"
                echo "##vso[task.setvariable variable=$key]$value"
            fi
            ;;
        'shell')
            # Default shell export
            export "$key=$value"
            ;;
        esac
    fi
done < "$OUTPUT_FILE"
