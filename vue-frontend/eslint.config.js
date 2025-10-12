import pluginVue from 'eslint-plugin-vue'
import js from '@eslint/js'

export default [
  js.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.{js,mjs,cjs,vue}'],
    languageOptions: {
      globals: {
        MathJax: 'readonly'
      }
    },
    rules: {
      'vue/multi-word-component-names': 'off',
      'no-unused-vars': 'warn',
      'vue/no-unused-vars': 'warn'
    }
  },
  {
    ignores: ['dist/**', 'node_modules/**', 'build/**', 'public/mathjax/**']
  }
]
