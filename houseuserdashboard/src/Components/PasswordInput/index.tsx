import { useState } from 'react'

const PasswordInput = ({ onChange, title, placeholder }: { onChange: Function; title: string; placeholder: string }) => {
  const [Show, setShow] = useState(false)

  return (
    <>
      {title && <label>{title}</label>}
      <div className="" style={{ display: 'flex', flexDirection: 'row' }}>
        <input
          className="form-control"
          type={Show ? 'input' : 'password'}
          style={{ borderTopRightRadius: '0', borderBottomRightRadius: '0' }}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
        />
        <button
          className="btn border"
          style={{ margin: '0px', padding: '0px', width: '42px', borderTopLeftRadius: '0', borderBottomLeftRadius: '0', boxShadow: 'none' }}
          onClick={() => setShow(!Show)}
        >
          <i className={`fa fa-eye${Show ? '-slash' : ''}`} />
        </button>
      </div>
    </>
  )
}

export default PasswordInput
