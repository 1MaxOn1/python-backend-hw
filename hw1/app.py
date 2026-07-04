from typing import Any, Awaitable, Callable
from http import HTTPStatus

async def application(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
):
    """
    Args:
        scope: Словарь с информацией о запросе
        receive: Корутина для получения сообщений от клиента
        send: Корутина для отправки сообщений клиенту
    """
    # TODO: Ваша реализация здесь
    if 'path' in scope.keys():
        curr_path = scope['path']
    else:
        curr_path = None
    
    a, b = 0, 1
    
    sum_mean = 0
    
    start_send = {
        'type': 'http.response.start',
        'status': 200,
        'headers':[
            [b'content-type', b'text/plain']
        ]
    }
    
    end_send = None
    
    if curr_path and curr_path.split('/')[1] == 'fibonacci':
        num_fib = curr_path.split('/')[2]
        
        try:
            num_fib = int(num_fib)
        except Exception:
            await send(
                {
                    'type': 'http.response.start',
                    'status':422,
                    'headers':[
                        [b'content-type', b'text/plain']
                    ]
                }
            )
            await send({'type':'http.response.body', 'body':'incorrect value'.encode('utf-8')})
            return
        
        if num_fib < 0:
            await send(
                {
                    'type': 'http.response.start',
                    'status':400,
                    'headers':[
                        [b'content-type', b'text/plain']
                    ]
                }
            )
            await send({'type':'http.response.body', 'body':'incorrect value'.encode('utf-8')})
            return
            
        
        for i in range(num_fib):
            a, b = b, a+b
        
        fib_response = {
            'type':'http.response.body',
            'body': ('{"result":' + str(a) + '}').encode('utf-8')
        }
        
        end_send = fib_response
    
    elif curr_path and curr_path.split('/')[1] == 'factorial':
        num_fact = str(scope['query_string']).split('=')[-1].replace('\'', '')

        try:
            num_fact = int(num_fact)
        except Exception:
            mean_response = {
                    'type':'http.response.body',
                    'body':'incorrect number'.encode('utf-8')
                }
            await send(
                {
                    'type':'http.response.start',
                    'status':422,
                    'headers':[
                        [b'content-type', b'text/plain']
                    ]
                }
            )
            await send({'type':'http.response.body', 'body':'incorrect value'.encode('utf-8')})
            return

        if num_fact < 0:
            await send(
                {
                    'type':'http.response.start',
                    'status':400,
                    'headers':[
                        [b'content-type', b'text/plain']
                    ]
                }
            )
            await send({'type':'http.response.body', 'body':'incorrect value'.encode('utf-8')})
            
            return
        
        for i in range(1, num_fact+1):
            b *= i     
                
        factorial_response = {
            "type": "http.response.body",
            "body": ('{"result":' + str(b) + '}').encode("utf-8"),
        }
        
        end_send = factorial_response
        b = 1
        
    elif curr_path and curr_path.split('/')[1] == 'mean':
        body_in = await receive()
        
        vals = str(body_in['body']).replace('\'', '').replace('b', '')
        
        if vals == 'null':
            await send(
                {
                    'type':'http.response.start',
                    'status':422,
                    'headers':[
                        [b'content-type', b'text/plain']
                    ]
                }
            )
            await send({'type':'http.response.body', 'body': 'add query params'.encode('utf-8')})
            return
        
        vals = eval(vals)
        
        if len(vals) == 0:
            await send(
                {
                    'type':'http.response.start',
                    'status':400,
                    'headers':[
                        [b'content-type', b'text/plain']
                    ]
                }
            )
            
            await send({'type':'http.response.body', 'body': 'not enough values'.encode('utf-8')})
            return
        
        in_vals = str(scope['query_string'])
        in_vals = in_vals.replace('\'', '')[1:]
        
        for i in vals:
            try:
                sum_mean += i
            except Exception:
                mean_response = {
                    'type':'http.response.body',
                    'body':'incorrect number'.encode('utf-8')
                }
                await send(
                    {
                        'type':'http.response.start',
                        'status':422,
                        'headers':[
                            [b'content-type', b'text/plain']
                        ]
                    }
                )
                await send({'type':'http.response.body', 'body':'incorrect value'})
                return                 
        
        if sum_mean: 
            sum_mean /= len(vals)

            value = str(sum_mean)
            
            mean_response = {
                'type': 'http.response.body',
                'body': ('{"result":' + value + '}').encode('utf-8')
            }
        
        end_send = mean_response
    
    else:
        start_send = {
            'type': 'http.response.start',
            'status': 404,
            'headers':[
                [b'content-type', b'text/plain']
            ]
        }
        
        no_path = {
            'type': 'http.response.body',
            'body': 'No response'.encode('utf-8')
        }
        end_send = no_path
        
    await send(start_send)
    await send(end_send)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:application", host="0.0.0.0", port=8000, reload=True)