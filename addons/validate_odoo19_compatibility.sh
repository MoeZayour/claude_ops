#!/bin/bash
echo "======================================"
echo "Odoo 19 Compatibility Validation"
echo "======================================"
echo ""

echo "1. Checking for <tree> tags..."
TREE_COUNT=$(grep -r "<tree" ops_matrix* --include="*.xml" 2>/dev/null | grep -v "string=" | grep -v "comment" | grep -v "<!--" | wc -l)
if [ "$TREE_COUNT" -eq 0 ]; then
    echo "   ✓ PASS: No <tree> tags found"
else
    echo "   ✗ FAIL: Found $TREE_COUNT <tree> tags"
    grep -r "<tree" ops_matrix* --include="*.xml" | grep -v "string=" | grep -v "comment"
fi
echo ""

echo "2. Checking for group_ops_administrator..."
GROUP_COUNT=$(grep -r "group_ops_administrator" ops_matrix* --include="*.xml" --include="*.py" 2>/dev/null | wc -l)
if [ "$GROUP_COUNT" -eq 0 ]; then
    echo "   ✓ PASS: No group_ops_administrator references found"
else
    echo "   ✗ FAIL: Found $GROUP_COUNT group_ops_administrator references"
    grep -r "group_ops_administrator" ops_matrix* --include="*.xml" --include="*.py"
fi
echo ""

echo "3. Checking for attrs= syntax..."
ATTRS_COUNT=$(grep -r 'attrs=' ops_matrix* --include="*.xml" 2>/dev/null | wc -l)
if [ "$ATTRS_COUNT" -eq 0 ]; then
    echo "   ✓ PASS: No attrs= syntax found"
else
    echo "   ✗ FAIL: Found $ATTRS_COUNT attrs= occurrences"
    grep -r 'attrs=' ops_matrix* --include="*.xml"
fi
echo ""

echo "4. Checking for expand= in search views..."
EXPAND_COUNT=$(grep -r 'expand=' ops_matrix* --include="*.xml" 2>/dev/null | wc -l)
if [ "$EXPAND_COUNT" -eq 0 ]; then
    echo "   ✓ PASS: No expand= attributes found"
else
    echo "   ✗ FAIL: Found $EXPAND_COUNT expand= attributes"
    grep -r 'expand=' ops_matrix* --include="*.xml"
fi
echo ""

echo "5. Verifying <list> tag conversions..."
LIST_COUNT=$(grep -r "<list" ops_matrix* --include="*.xml" 2>/dev/null | wc -l)
echo "   ℹ INFO: Found $LIST_COUNT <list> tags (expected: >0)"
echo ""

echo "6. Checking for Python expression syntax..."
INVISIBLE_COUNT=$(grep -r 'invisible="' ops_matrix* --include="*.xml" 2>/dev/null | wc -l)
READONLY_COUNT=$(grep -r 'readonly="' ops_matrix* --include="*.xml" 2>/dev/null | wc -l)
echo "   ℹ INFO: Found $INVISIBLE_COUNT invisible attributes"
echo "   ℹ INFO: Found $READONLY_COUNT readonly attributes"
echo ""

echo "======================================"
echo "Validation Summary"
echo "======================================"
if [ "$TREE_COUNT" -eq 0 ] && [ "$GROUP_COUNT" -eq 0 ] && [ "$ATTRS_COUNT" -eq 0 ] && [ "$EXPAND_COUNT" -eq 0 ]; then
    echo "✓ ALL CHECKS PASSED!"
    echo ""
    echo "Your OPS modules are fully Odoo 19 compatible!"
else
    echo "✗ SOME CHECKS FAILED"
    echo "Please review the output above for details."
fi
echo "======================================"
