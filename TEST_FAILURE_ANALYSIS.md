# Test Failure Analysis

After running all tests, there are **245 failures** and **213 passes**. Here's a breakdown of the main issues:

## 1. Duplicate Test Files (FIXED)
- ❌ `app/test/unit/models/test_Climate.py` (duplicate - removed)
- ❌ `app/test/unit/models/test_Flora.py` (duplicate - removed)
- ✅ Correct locations: `app/test/unit/models/Climate/test_Climate.py` and `app/test/unit/models/Flora/test_Flora.py`

## 2. API Changes - Test Parameter Mismatches

### Fauna Tests (Many failures - ~70 tests)
**Issue**: Tests use `avg_feet_area` but code uses `avg_foot_area`
- Pattern: `TypeError: Fauna.__init__() got an unexpected keyword argument 'avg_feet_area'. Did you mean 'avg_foot_area'?`
- **Fix**: Search and replace `avg_feet_area` → `avg_foot_area` in test files:
  - `app/test/unit/models/Fauna/test_Fauna.py`
  - `app/test/unit/models/Fauna/test_Predator.py`
  - `app/test/unit/models/Fauna/test_Prey.py`

### Flora Tests (Many failures - ~60 tests)
**Issue**: Tests use `total_mass` parameter but Flora API changed to use `avg_mass` + `population`
- Pattern: `TypeError: Flora.__init__() got an unexpected keyword argument 'total_mass'`
- **Fix**: Need to update Flora test constructors to use new API
- Files affected:
  - `app/test/unit/models/Flora/test_Flora.py`
  - `app/test/unit/models/Flora/test_Shrub.py`
  - `app/test/unit/models/Flora/test_Tree.py`

### Flora isinstance() Errors (~30 tests)
**Issue**: `TypeError: isinstance() arg 2 must be a type, a tuple of types, or a union`
- Files: `test_Grass.py`, `test_Moss.py`
- **Fix**: Check `isinstance()` calls - might be using string instead of type

## 3. Climate Class Changes (~10 failures)
**Issues**:
- Missing `loaders` attribute: `AttributeError: 'Climate' object has no attribute 'loaders'`
- Missing methods: `get_current_SSRD`, `get_current_rainfall`
- Different error messages for day validation
- Static method changes: `test_2mtemp_change_from_snow_delta_static_method`, `test_soil_temp_change_from_snow_delta_static_method`
- `is_steppe()` method disabled/removed
- `is_permafrost()` behavior changed

**Fix**: Update tests to match current Climate API

## 4. Climate Driver Parameter Changes (~5 failures)
**Issue**: Tests use `biome_offset` but code might use different parameter name
- Files: All climate driver test files
- Pattern: `TypeError: ...generate_daily_...() got an unexpected keyword argument 'biome_offset'`

**Fix**: Check actual parameter names in driver classes

## 5. Data Loader Tests (~30 failures)
**Issue**: All data loader tests fail because data structure doesn't match expectations
- Pattern: `AssertionError: Lists differ: [] != [0, 1]` or `IndexError: list index out of range`
- Files: All `test_*Loader.py` files

**Fix**: Update tests to match actual data loader behavior or skip if data not available

## 6. PlotGrid Tests (~3 failures)
**Issues**:
- `test_update_all_plots_staggered_updates`: Update schedule changed
- `test_visualize_biomes_basic`: Mock issue with iterables
- `test_over_predator_capacity_over_limit`: Predator capacity check disabled

**Fix**: Update to match current implementation

## 7. Grid Initializer Tests (~3 failures)
**Issues**:
- Missing `predators` key in `biome_defaults`
- `_create_prey` only supports mammoths now, not other prey types
- `_add_default_fauna` behavior changed

**Fix**: Update tests to reflect that only mammoths are supported now

## Recommended Fix Order

1. ✅ **Fixed**: Remove duplicate test files
2. **Quick wins**: Fix `avg_feet_area` → `avg_foot_area` (simple find/replace)
3. **Medium effort**: Update Climate tests (check what methods actually exist)
4. **Medium effort**: Fix Grid Initializer tests (reflect mammoth-only support)
5. **High effort**: Update Flora tests (API change requires understanding new structure)
6. **Low priority**: Data loader tests (might need actual data files)

## Quick Commands

```bash
# Run only passing tests to see what works
python run_tests.py --tb=no -q | grep PASSED

# Run only unit tests (faster)
python run_tests.py unit

# Run only integration tests
python run_tests.py integration

# Run specific test file
python -m pytest app/test/unit/models/Plot/test_PlotGrid_migration.py -v
```

