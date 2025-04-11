import React, { useState } from 'react';

import { SearchBar as RNESearchBar, makeStyles, useTheme, Icon } from '@rneui/themed';
import { debounce } from 'lodash';
import { View, TouchableOpacity } from 'react-native';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  debounceMs?: number;
  autoFocus?: boolean;
  showClear?: boolean;
  onClear?: () => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = 'Search...',
  debounceMs = 300,
  autoFocus = false,
  showClear = true,
  onClear,
}) => {
  const [query, setQuery] = useState('');
  const styles = useStyles();
  const { theme } = useTheme();

  const debouncedSearch = React.useCallback(
    debounce((searchQuery: string) => {
      onSearch(searchQuery);
    }, debounceMs),
    [onSearch, debounceMs]
  );

  const handleChange = (text: string) => {
    setQuery(text);
    debouncedSearch(text);
  };

  const handleClear = () => {
    setQuery('');
    onClear?.();
  };

  return (
    <View style={styles.container}>
      <RNESearchBar
        platform="default"
        placeholder={placeholder}
        onChangeText={handleChange}
        value={query}
        autoFocus={autoFocus}
        containerStyle={styles.searchContainer}
        inputContainerStyle={styles.inputContainer}
        inputStyle={styles.input}
        searchIcon={
          <Icon
            name="search"
            type="material"
            size={20}
            color={theme.colors.grey2}
          />
        }
        clearIcon={
          showClear && query
            ? {
                type: 'material',
                name: 'close',
                size: 20,
                color: theme.colors.grey2,
                onPress: handleClear
              }
            : undefined
        }
      />
    </View>
  );
};

const useStyles = makeStyles((theme) => ({
  container: {
    marginBottom: theme.spacing.md,
  },
  searchContainer: {
    backgroundColor: 'transparent',
    borderTopWidth: 0,
    borderBottomWidth: 0,
    paddingHorizontal: 0,
  },
  inputContainer: {
    backgroundColor: theme.colors.grey5,
    borderRadius: theme.borderRadius.md,
    height: 40,
  },
  input: {
    fontSize: theme.fontSize.md,
    color: theme.colors.grey1,
  },
}));
