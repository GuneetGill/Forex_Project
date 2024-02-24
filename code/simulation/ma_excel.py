import pandas as pd

WIDTHS = {
    'L:L' : 20,
    'B:F' : 9
}

#function for ensuing the colmns are not squished when opening excel sheet
def set_widths(pair, writer):
    worksheet = writer.sheets[pair]
    for k,v in WIDTHS.items():
        worksheet.set_column(k, v)

#book is the excel workbook created
#start and end row are parameters for range of row data
#label_col and data_col specfiy the columns for x and y axis
#title is name of chart and sheetname is the name of the sheet
def get_line_chart(book, start_row, end_row, labels_col, data_col, title, sheetname):

    #create chart object using add_chart method
    chart = book.add_chart({'type' : 'line'})
    
    chart.add_series({
        'categories' : [sheetname, start_row, labels_col, end_row, labels_col],
        'values' : [sheetname, start_row, data_col, end_row, data_col],
        'line' : {'color' : 'blue'}
    })

    chart.set_title({'name' : title})
    chart.set_legend({'none' : True})
    return chart

#name of pair and cross, the dataframe and writer object
def add_chart(pair, cross, df, writer):
    #get workbook 
    workbook = writer.book
    #sheet in workbook and each pair has its own sheet
    worksheet = writer.sheets[pair]

    #create line chart, start at row 1 since index starts at 0 and we 2nd row 
    #which is row 1

    #labels colums are 11 and 12 
    chart = get_line_chart(workbook, 1, df.shape[0], 11, 12, 
                           f"GAIN_C for {pair} {cross}", pair )
    
    #we want to scale chart to make it bigger
    chart.set_size({'x_scale' : 2.5, 'y_scale' : 2.5})
    #O letter o 1
    worksheet.insert_chart('O1', chart)


def add_pair_charts(df_ma_res, df_ma_trades, writer):
    #we want to only show the gain and time col on our chart 
    cols = ['time', 'GAIN_C']

    #drop_druplicates drops all duplicates and removes all druplicate rows
    #lets you also specfiy so if we did subset="ma_l" it would drop all 
    #ones with ma_150 for example
    #so now we just want to keep first row since that was the best one
    #so if we remove subset by pair it will remove all other pairs with the same name
    #which would be all of them and this will be stored in temp dataframe
    df_temp = df_ma_res.drop_duplicates(subset="pair")

    #df_temp is dataframe is just a df with first row all made into one gaint table with
    #all of the best of each pair

    #_, is python convenient when u dont use the value
    for _, row in df_temp.iterrows():
        #temp dataframe
        dft = df_ma_trades[(df_ma_trades.cross == row.cross)&
                            (df_ma_trades.pair == row.pair)]
        dft[cols].to_excel(writer, sheet_name=row.pair, index=False,startrow=0,startcol=11 )
        # it will start at A1 but we want it to be fruther 
        set_widths(row.pair, writer)
        add_chart(row.pair, row.cross, dft, writer)

#create a sheet for each pair 
def add_pair_sheets(df_ma_res, writer):
    #this data is in decending and abc order and is sorted
    #create new sheet with excel sheet 
    for p in df_ma_res.pair.unique():
        tdf = df_ma_res[df_ma_res.pair == p]
        tdf.to_excel(writer, sheet_name=p, index=False)

#pairs should be in abc order and gains are in decending order
def prepare_data(df_ma_res, df_ma_trades):
    #sort
    df_ma_res.sort_values(
        by=['pair', 'total_gain'], 
        ascending=[True, False],
        inplace=True)
    #remove time zone since it can causes issues sometimes 
    #set the timezone to None 
    df_ma_trades['time'] = [ x.replace(tzinfo=None) for x in df_ma_trades['time']]
    
#filtered dataframes 
def process_data(df_ma_res, df_ma_trades, writer):
    prepare_data(df_ma_res, df_ma_trades)
    add_pair_sheets(df_ma_res, writer)
    add_pair_charts(df_ma_res, df_ma_trades, writer)

#send both dataframe and the granularity 
def create_excel(df_ma_res, df_ma_trades, granularity):

    #filename of excel file I want to create
    filename = f"ma_sim_{granularity}.xlsx"
    #used for writing excel files
    #filename: name of excel file u want to create or modidy
    #engine this is the excel writer engine. 
    writer = pd.ExcelWriter(filename,  engine="xlsxwriter")
    
    #send in orginal data with granulaity
    process_data(
        df_ma_res[df_ma_res.granularity == granularity].copy(), 
        df_ma_trades[df_ma_trades.granularity == granularity].copy(), 
        writer)
    
    #used to save excel sheet
    writer.close()


def create_ma_res(granularity):
    df_ma_res = pd.read_pickle("./data/ma_res.pkl")
    df_ma_trades = pd.read_pickle("./data/ma_trades.pkl")
    create_excel(df_ma_res, df_ma_trades, granularity)

if __name__ == "__main__":
    
    #send in dataframes
    df_ma_res = pd.read_pickle("../data/ma_res.pkl")
    df_ma_trades = pd.read_pickle("../data/ma_trades.pkl")

    create_excel(df_ma_res, df_ma_trades, "H1")
    create_excel(df_ma_res, df_ma_trades, "H4")