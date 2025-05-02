import yfinance as yf
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
# Global store for plotting
stored_data = {}

def fetch_data():
    tickers_input = entry.get().strip()
    if not tickers_input:
        messagebox.showwarning("Input Error", "Enter at least one stock ticker.")
        return

    tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
    result_text.delete("1.0", tk.END)
    stored_data.clear()

    try:
        usd_inr = yf.Ticker("USDINR=X").history("1d")['Close'].iloc[-1]
    except Exception:
        messagebox.showerror("Error", "Couldn't fetch USD to INR rate.")
        return
 
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history("max")
            if hist.empty:
                result_text.insert(tk.END, f"{ticker} - ❌ No data.\n\n")
                continue

            last_price = hist['Close'].iloc[-1]
            converted = not ticker.endswith(".NS")
            inr_price = last_price * usd_inr if converted else last_price

            # Store for plotting
            stored_data[ticker] = {
                "all": hist['Close'],
                "converted": converted,
                "usd_inr": usd_inr
            }

            # Display info
            result_text.insert(tk.END, f"{info.get('longName', ticker)}\n")
            result_text.insert(tk.END, f"Sector        : {info.get('sector', 'N/A')}\n")
            result_text.insert(tk.END, f"Current Price : ₹{inr_price:.2f}\n")
            result_text.insert(tk.END, f"52W High / Low: ₹{info.get('fiftyTwoWeekHigh', 'N/A')*(usd_inr):.2f}/₹{info.get('fiftyTwoWeekLow', 'N/A')*usd_inr:.2f}\n")
            result_text.insert(tk.END, f"Market Cap    : ₹{info.get('marketCap', 0) / 1e7:.2f} Cr\n")
            result_text.insert(tk.END, f"P/E Ratio     : {info.get('trailingPE', 'N/A')}\n")
            result_text.insert(tk.END, f"Dividend Yield: {info.get('dividendYield', 0) :.2f}%\n")
            result_text.insert(tk.END, "-" * 60 + "\n\n")

        except Exception as e:
            result_text.insert(tk.END, f"{ticker} - ⚠️ Error: {e}\n")

    plot_data()

def get_range(series, label):
    end_date = series.index[-1] 

    if label == "Last Week":
        start_date = end_date - timedelta(days=7)
    elif label == "Last Month":
        start_date = end_date - timedelta(days=30)
    elif label == "Last Year":
        start_date = end_date - timedelta(days=365)
    else:
        return series

    return series.loc[start_date:end_date]

def plot_data():
    if not stored_data:
        messagebox.showinfo("No Data", "Fetch stock data first.")
        return

    fig, ax = plt.subplots(figsize=(12, 4))
    selected = range_var.get()

    for ticker, data in stored_data.items():
        series = get_range(data["all"], selected)
        values = series * data["usd_inr"] if data["converted"] else series
        ax.plot(series.index, values, label=f"{ticker} ({selected})")

    ax.set(title=f"Stock Performance – {selected}", xlabel="Date", ylabel="Price (₹)")
    ax.legend(), ax.grid(True)

    for widget in chart_frame.winfo_children():
        widget.destroy()
    FigureCanvasTkAgg(fig, master=chart_frame).get_tk_widget().pack()

# GUI Setup
root = tk.Tk()
root.title("📈 Stock Viewer")
root.geometry("700x700")

tk.Label(root, text="Enter stock tickers (comma separated):", font=('Arial', 12)).pack(pady=10)
entry = tk.Entry(root, width=50, font=('Arial', 12))
entry.pack(pady=5)

tk.Button(root, text="Get Stock Info & Graph", command=fetch_data, bg="green", fg="black", font=('Arial', 12)).pack(pady=10)

range_var = tk.StringVar(value="Last Week")
tk.OptionMenu(root, range_var, "Last Week", "Last Month", "Last Year", "All Time", command=lambda _: plot_data()).pack(pady=5)

result_text = tk.Text(root, height=14, font=('Courier', 10), bg="White")
result_text.pack(padx=10, fill=tk.X)

chart_frame = tk.Frame(root)
chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()
