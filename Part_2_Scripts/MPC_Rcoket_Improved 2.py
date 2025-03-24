import numpy as np
import casadi as ca
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import math

class MPC:
    def __init__(self, solver: str):
        self.G = 6.67430e-11
        self.M = 5.972e24
        self.R = 8371000.0  
        self.M = 5.972e24
        self.g = 9.81
        self.m = 30.0
        self.ell = 13.0
        self.radius = 5.0
        self.J = 0.25 * self.m * self.radius**2 + 1/12 * self.m * self.ell**2

        self.F_g = self.G * self.M * self.m / self.R**2

        #CONSTRAINTS
        self.umin = [-900, -math.pi/4, -200]
        self.umax = [900, math.pi/4, 200]

        #MPC TUNING
        self.h = 0.05
        self.Nh = 20
        self.nx = 6    
        self.nu = 3   

        #SETTING VARIABLES FOR CASADI
        self.opti = ca.Opti()
        self.X = self.opti.variable(self.nx, self.Nh+1)  
        self.U = self.opti.variable(self.nu, self.Nh)     
        self.e0 = self.opti.parameter(self.nx)              

        self.xref_param = self.opti.parameter(self.nx)
        self.ymin = [0]

        self.Q = np.diag([1000, 1000, 3000, 10, 10, 100000])  
        self.R = np.diag([0.1, 1, 0.1])  
        self.Qf = np.diag([1000, 1000, 2000, 100, 100, 100000])

        self.solver = solver

        self.define_mpc()  
        self.opti.solver(solver)  

    def dynamics(self, x, u):
        x_dot = x[3]
        y_dot = x[4]
        theta_dot = x[5]

        torque = u[0] * ca.sin(u[1]) + u[2]

        x_ddot = u[0] / self.m * ca.cos(x[2] + u[1]) - u[2]*ca.sin(x[2])/self.m
        y_ddot = (u[0] / self.m * ca.sin(x[2] + u[1])) - ( self.G * self.M/ ((8371000000.0 + x[1]*1000000)**2))  + ((x_dot)**2 / (8371000000.0 + x[1]*1000000) ) + u[2]*ca.cos(x[2])/self.m
        theta_ddot = (self.ell / (2 * self.J)) * torque

        return ca.vertcat(x_dot, y_dot, theta_dot, x_ddot, y_ddot, theta_ddot)

    def rk4_step(self, x, u, dt):
        #runge-kutta-4 algorihm to solve dynamics
        k1 = self.dynamics(x, u)
        k2 = self.dynamics(x + dt / 2 * k1, u)
        k3 = self.dynamics(x + dt / 2 * k2, u)
        k4 = self.dynamics(x + dt * k3, u)
        return x + (dt / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

    def define_mpc(self):
        self.opti.subject_to(self.X[:, 0] == self.e0)
        cost = 0

        for k in range(self.Nh):
            x_next = self.rk4_step(self.X[:, k], self.U[:, k], self.h)
            self.opti.subject_to(self.X[:, k + 1] == x_next)

            #COST FUNCTION
            cost += ca.mtimes([(self.X[:, k] - self.xref_param).T, self.Q, (self.X[:, k] - self.xref_param)])[0, 0]
            cost += ca.mtimes([self.U[:, k].T, self.R, self.U[:, k]])[0, 0]
            cost += ca.mtimes([(self.X[:, self.Nh] - self.xref_param).T, self.Qf, (self.X[:, self.Nh] - self.xref_param)])[0, 0]

            #CONSTRAINTS
            self.opti.subject_to(ca.vertcat(*self.umin) <= self.U[:, k])
            self.opti.subject_to(self.U[:, k] <= ca.vertcat(*self.umax))
            self.opti.subject_to(self.X[1, k] >= self.ymin[0])


        #TERMINAL COST
        cost += ca.mtimes([(self.X[:, self.Nh] - self.xref_param).T, self.Qf, (self.X[:, self.Nh] - self.xref_param)])[0, 0]
        self.opti.minimize(cost)

    def solve_mpc(self, x0, x_ref):
        self.opti.set_value(self.e0, x0)
        self.opti.set_value(self.xref_param, x_ref)
        sol = self.opti.solve()
        return np.array(sol.value(self.U[:, 0]))


class Simulator:
    def __init__(self, mpc, x_refs, threshold=0.01):
        self.mpc = mpc
        self.Tfinal = 12.0
        self.Nt = int(self.Tfinal / self.mpc.h)
        self.t_hist = np.linspace(0, self.Tfinal, self.Nt)
        self.xhist = np.zeros((self.mpc.nx, self.Nt))
        self.uhist = np.zeros((self.mpc.nu, self.Nt - 1))
        self.x_refs = x_refs
        self.threshold = threshold

        #initial state vector
        self.xhist[:, 0] = np.array([0, 0, 0, 10, 0, 0])
        self.current_ref_index = 0


    def run_simulation(self):
        for k in range(self.Nt - 1):
            current_ref = self.x_refs[self.current_ref_index]
            error = np.linalg.norm(self.xhist[:2, k] - current_ref[:2])
            if error < self.threshold and self.current_ref_index < len(self.x_refs) - 1:
                self.current_ref_index += 1
                current_ref = self.x_refs[self.current_ref_index]
                print(f"Switching to reference {self.current_ref_index} at time {self.t_hist[k]:.2f}s")
            u = self.mpc.solve_mpc(self.xhist[:, k], current_ref)
            self.uhist[:, k] = u
            self.xhist[:, k + 1] = np.array(self.mpc.rk4_step(self.xhist[:, k], u, self.mpc.h)).flatten()


    def plotter(self):

        plt.figure()
        plt.plot(self.t_hist, self.xhist[0, :], label='x')
        plt.plot(self.t_hist, self.xhist[1, :], label='y')
        plt.plot(self.t_hist, self.xhist[2, :], label='theta')
        plt.legend()
        plt.xlabel('Time [s]')
        plt.ylabel('State')
        plt.title('State Trajectory')
        plt.grid()
        plt.show()

        plt.figure()
        plt.plot(self.xhist[0, :], self.xhist[1, :], 'b-', label='Trajectory')

        refs_x = [ref[0] for ref in self.x_refs]
        refs_y = [ref[1] for ref in self.x_refs]
        plt.plot(refs_x, refs_y, 'r*', markersize=12, label='References')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.title('Trajectory in the x-y Plane')
        plt.legend()
        plt.grid()
        plt.show()


    def animate(self):

        x_min, x_max = self.xhist[0, :].min() - 10, self.xhist[0, :].max() + 10
        y_min, y_max = self.xhist[1, :].min() - 10, self.xhist[1, :].max() + 10

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_aspect('equal')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("Rocket Trajectory Animation")

        ax.axhline(y=self.xhist[1, 0], linestyle='--', color='gray', label='Start Y')
        ax.axhline(y=self.x_refs[-1][1], linestyle='--', color='gray', label='Reference Y')
        
        refs_x = [ref[0] for ref in self.x_refs]
        refs_y = [ref[1] for ref in self.x_refs]
        ax.plot(refs_x, refs_y, '*', color= 'gold' ,markersize=12, label='References')
        
        body_width = 3
        body_height = 10

        rocket_body = patches.Rectangle((-body_width/2, -body_height/2), body_width, body_height,
                                        fc="white", ec="black")
        ax.add_patch(rocket_body)
        
        nose_coords = np.array([[-body_width/2, body_height/2],
                                [ body_width/2, body_height/2],
                                [0, body_height/2 + 5]])
        rocket_nose = patches.Polygon(nose_coords, closed=True, fc="white", ec="black")
        ax.add_patch(rocket_nose)
        
        traj_line, = ax.plot([], [], '--', color = 'gray' ,label='Trajectory')

        def update(frame):
            state = self.xhist[:, frame]
            x_pos, y_pos, theta = state[0], state[1], state[2] - math.pi/2
   
            transform = plt.matplotlib.transforms.Affine2D().rotate(theta).translate(x_pos, y_pos)
            rocket_body.set_transform(transform + ax.transData)
            rocket_nose.set_transform(transform + ax.transData)
            
            traj_line.set_data(self.xhist[0, :frame+1], self.xhist[1, :frame+1])
            return rocket_body, rocket_nose, traj_line

        ani = animation.FuncAnimation(fig, update, frames=self.Nt, interval=50,
                                        blit=True, repeat=True, repeat_delay=2000)
        plt.legend()
        plt.show()


if __name__ == '__main__':
    mpc = MPC('ipopt')
    x_refs = [
        np.array([150, 100, math.pi / 4, 10, 0, 0]),
        np.array([200, 130, math.pi / 5, 10, 0, 0]),
        np.array([240, 145, math.pi / 7, 10, 0, 0]),
        np.array([290, 160, 0, 200, 0, 0]),
        np.array([340, 160, 0, 200, 0, 0]),
        np.array([390, 160, 0, 200, 0, 0]),
        np.array([440, 160, 0, 200, 0, 0]),
        np.array([490, 160, 0, 200, 0, 0]),
        np.array([540, 160, 0, 200, 0, 0])
    ]
    sim = Simulator(mpc, x_refs, threshold=20.0)
    sim.run_simulation()
    sim.plotter()
    sim.animate()