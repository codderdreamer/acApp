import { createSlice, isAnyOf } from '@reduxjs/toolkit'
import { GetUserThunk } from './thunks'
import { UserInitialState } from './models'

const AccountSlice = createSlice({
  name: 'accountSlice',
  initialState: UserInitialState,
  reducers: {
    ResetUser: (state) => {
      Object.assign(state, UserInitialState)
    }
  },
  extraReducers(builder) {
    builder
      .addMatcher(isAnyOf(GetUserThunk.pending), (state) => {
        state.loading = true
      })
      .addMatcher(isAnyOf(GetUserThunk.fulfilled), (state, action) => {
        state.loading = false
        state.data = action.payload.data
      })
      .addMatcher(isAnyOf(GetUserThunk.rejected), (state, action) => {
        state.loading = false
        localStorage.removeItem('access_token') // surekli istek atmasin diye
        state.error = action.payload as string
      })
  }
})

export const { ResetUser } = AccountSlice.actions
export default AccountSlice.reducer
