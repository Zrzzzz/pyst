/**
 * 信息页面 - 个人名片
 */
import React from 'react'
import ThemeToggle from '@/components/ThemeToggle'
import './Info.scss'

export const Info: React.FC = () => {
  const skills = ['React', 'TypeScript', 'Vite', 'SCSS', 'Python', 'Web Design']

  return (
    <div className="info-page">
      {/* 名片容器 */}
      <div className="card-container">
        <div className="card">
          {/* 头像 */}
          <div className="avatar-wrapper">
            <img
              src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
              alt="Avatar"
              className="avatar"
            />
          </div>

          {/* 名字 */}
          <h1 className="name">Your Name</h1>

          {/* 技能列表 */}
          <div className="skills-section">
            <h2 className="skills-title">Skills</h2>

            <div className="skills-grid">
              {skills.map((skill) => (
                <div key={skill} className="skill-tag">
                  {skill}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 主题切换按钮 */}
      <ThemeToggle />
    </div>
  )
}

export default Info

