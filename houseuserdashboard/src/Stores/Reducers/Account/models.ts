export interface UserModel {
  loading: boolean
  error: string
  data: any
}

export const UserInitialState: UserModel = {
  loading: false,
  error: '',
  data: {}
}
