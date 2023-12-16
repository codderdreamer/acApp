import { createAsyncThunk } from '@reduxjs/toolkit'
import { GetUserWithToken } from './services'

export const GetUserThunk = createAsyncThunk('GetUser', async (_, thunkApi) => {
  try {
    const response: any = await GetUserWithToken()
    return response
  } catch (error: any) {
    const message = error.message
    return thunkApi.rejectWithValue(message)
  }
})
